from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from main.models import UserProfile, Product, Category, ExercisePlan, NutritionPlan, Order, OrderItem, SupportRequest, Review, Post
from main.forms import LoginForm, SignUpForm, UserProfileForm, ReviewForm, PostForm
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe, json
from django.conf import settings
from django.http import HttpResponse
import os

def home(request):
    return render(request, 'main/home.html')


def favicon(request):
    favicon_path = os.path.join(settings.MEDIA_ROOT, 'favicon/favicon.ico')
    with open(favicon_path, 'rb') as favicon_file:
        return HttpResponse(favicon_file.read(), content_type="image/x-icon")

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def home(request):
    is_admin = request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False
    reviews = Review.objects.all().order_by('-created_at')[:2]
    posts = Post.objects.all().order_by('-created_at')[:2]
    return render(request, 'main/home.html', {
        'is_admin': is_admin,
        'reviews': reviews,
        'posts': posts
    })

def about(request):
    return render(request, 'main/about_us.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Check if the user is banned
            if user.groups.filter(name="Banned").exists():
                messages.error(request, "Your account has been banned. Please contact support.")
                return redirect('login')

            # Login the user
            login(request, user)
            return redirect('my_profile')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group, _ = Group.objects.get_or_create(name='User')  # Ensure group exists
            user.groups.add(group)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    user_group = user.groups.first()
    group_name = user_group.name if user_group else "User"
    return render(request, 'account/my_profile.html', {
        'user': user,
        'profile': profile,
        'group_name': group_name
    })


@login_required
def settings_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your personal information has been updated successfully.")
            return redirect('settings')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'account/settings.html', {'form': form})


@login_required
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Your email has been updated successfully.')
        else:
            messages.error(request, 'Please provide a valid email.')
    return redirect('settings')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif not request.user.check_password(current_password):
            messages.error(request, 'Your current password is incorrect.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password has been changed successfully.')
    return redirect('settings')


@login_required
def update_personal_info(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your personal information has been updated successfully.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    return redirect('settings')


# Review/Posts
@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})

@login_required
def my_posts(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'posts/my_posts.html', {'posts': posts})

@login_required
def create_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('my_reviews')
    else:
        form = ReviewForm()
    return render(request, 'reviews/create_review.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('my_posts')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('my_reviews')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/edit_review.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    return redirect('my_reviews')

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    post.delete()
    return redirect('my_posts')

def all_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'reviews/all_reviews.html', {'reviews': reviews})

def all_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/all_posts.html', {'posts': posts})

@login_required
@user_passes_test(is_admin)
def admin_manage_reviews(request):
    reviews = Review.objects.all()
    return render(request, 'admins/manage_reviews.html', {'reviews': reviews})

@login_required
@user_passes_test(is_admin)
def admin_manage_posts(request):
    posts = Post.objects.all()
    return render(request, 'admins/manage_posts.html', {'posts': posts})

@login_required
@user_passes_test(is_admin)
def admin_edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Logic for editing a post
    return render(request, 'admins/edit_post.html', {'post': post})

@login_required
@user_passes_test(is_admin)
def admin_delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('admin_manage_posts')

@login_required
@user_passes_test(is_admin)
def admin_edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    # Logic for editing a review
    return render(request, 'admins/edit_review.html', {'review': review})

@login_required
@user_passes_test(is_admin)
def admin_delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    return redirect('admin_manage_reviews')

# User content
@login_required
def my_content(request):
    user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    user_posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'account/my_content.html', {
        'user_reviews': user_reviews,
        'user_posts': user_posts
    })

# Admin Panel Views
@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'admins/dashboard.html')


@login_required
@user_passes_test(is_admin)
def admin_manage_users(request):
    users = User.objects.all()
    return render(request, 'admins/manage_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def admin_manage_groups(request):
    groups = Group.objects.all()
    permissions = Permission.objects.all()

    if request.method == "POST":
        group_name = request.POST.get("group_name")
        selected_permissions = request.POST.getlist("permissions")

        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            if selected_permissions:
                for perm_id in selected_permissions:
                    permission = Permission.objects.get(id=perm_id)
                    group.permissions.add(permission)
            messages.success(request, f"Group '{group_name}' created successfully.")
        return redirect("admin_manage_groups")

    return render(request, 'admins/manage_groups.html', {'groups': groups, 'permissions': permissions})


@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    groups = Group.objects.all()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        group_id = request.POST.get("group")

        user.username = username
        user.email = email

        if password:
            user.set_password(password)

        if group_id:
            group = Group.objects.get(pk=group_id)
            user.groups.clear()
            user.groups.add(group)

        user.save()
        messages.success(request, f"User {user.username} updated successfully.")
        return redirect("admin_manage_users")

    return render(request, "admins/edit_user.html", {"user": user, "groups": groups})


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, f"User {user.username} deleted successfully.")
    return redirect("admin_manage_users")


@login_required
@user_passes_test(is_admin)
def admin_edit_group(request, group_id):
    group = Group.objects.get(pk=group_id)
    permissions = Permission.objects.all()

    if request.method == "POST":
        group.name = request.POST.get("name", group.name)
        group.save()

        selected_permissions = request.POST.getlist("permissions")
        group.permissions.clear()
        for perm_id in selected_permissions:
            permission = Permission.objects.get(id=perm_id)
            group.permissions.add(permission)

        messages.success(request, f"Group '{group.name}' updated successfully.")
        return redirect("admin_manage_groups")

    return render(request, "admins/edit_group.html", {"group": group, "permissions": permissions})

@login_required
@user_passes_test(is_admin)
def admin_delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    group.delete()
    messages.success(request, f"Group {group.name} deleted successfully.")
    return redirect("admin_manage_groups")

def base_context_processor(request):
    is_banned = request.user.is_authenticated and request.user.groups.filter(name='Banned').exists()
    is_admin = request.user.is_authenticated and request.user.groups.filter(name='Admin').exists()

    return {
        'is_banned': is_banned,
        'is_admin': is_admin,
    }


# Shop Views
def shop_home(request):
    category_slug = request.GET.get('category', None)
    categories = Category.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()

    return render(request, 'shop/shop.html', {
        'categories': categories,
        'products': products,
        'selected_category': category_slug
    })
    
    #View for displaying products by selected category.
def shop_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'shop/shop.html', {
        'categories': categories,
        'products': products,
        'selected_category': category.slug
    })

def shop_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

def shop_cart(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        products.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })
        total_price += product.price * quantity

    context = {
        'products': products,
        'total_price': total_price
    }
    return render(request, 'account/cart.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    return redirect('shop_cart')


def checkout(request):
    if request.method == "POST":
        cart = request.session.get('cart', {}) 
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
            else:
                messages.error(request, f"{product.name} is out of stock.")
                return redirect('shop_cart')

        request.session['cart'] = {}
        messages.success(request, "Purchase completed successfully!")
        return redirect('shop_home')

    return render(request, 'shop/checkout.html')

@login_required
@user_passes_test(is_admin)
def admin_manage_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        slug = slugify(name)
        
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            Category.objects.create(name=name, description=description, slug=slug)
            messages.success(request, 'Category added successfully!')

        return redirect('admin_manage_categories')

    categories = Category.objects.all()
    return render(request, 'admins/manage_categories.html', {'categories': categories})


@login_required
@user_passes_test(is_admin)
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.slug = slugify(category.name)
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_manage_categories')

    return render(request, 'admins/edit_category.html', {'category': category})


@login_required
@user_passes_test(is_admin)
def admin_delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('admin_manage_categories')

@login_required
@user_passes_test(is_admin)
def admin_manage_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = get_object_or_404(Category, id=category_id)

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image,
        )
        messages.success(request, "Product added successfully!")
        return redirect("admin_manage_products")

    return render(request, "admins/manage_products.html", {"products": products, "categories": categories})


@login_required
@user_passes_test(is_admin)
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        
        category_id = request.POST.get("category")
        if category_id:
            product.category = get_object_or_404(Category, id=category_id)
        
        if "image" in request.FILES:
            product.image = request.FILES.get("image")

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("admin_manage_products")

    return render(request, "admins/edit_product.html", {
        "product": product,
        "categories": categories
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("admin_manage_products")

@login_required
@user_passes_test(is_admin)
def admin_manage_exercise_plans(request):
    exercise_plans = ExercisePlan.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')

        ExercisePlan.objects.create(
            name=name,
            description=description,
            price=price,
            duration=duration
        )
        messages.success(request, 'Exercise Plan added successfully!')
        return redirect('admin_manage_exercise_plans')

    return render(request, 'admins/manage_exercise_plans.html', {'exercise_plans': exercise_plans})
    
@login_required
@user_passes_test(is_admin)
def admin_manage_nutrition_plans(request):
    nutrition_plans = NutritionPlan.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration = request.POST.get('duration')

        NutritionPlan.objects.create(
            name=name,
            description=description,
            price=price,
            duration=duration
        )
        messages.success(request, 'Nutrition Plan added successfully!')
        return redirect('admin_manage_nutrition_plans')

    return render(request, 'admins/manage_nutrition_plans.html', {'nutrition_plans': nutrition_plans})
    
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

# Plans views
def exercise_plans(request):
    plans = ExercisePlan.objects.all()
    return render(request, 'plans/exercise_plans.html', {'exercise_plans': plans})


def exercise_plan_detail(request, plan_id):
    exercise_plan = get_object_or_404(ExercisePlan, id=plan_id)
    return render(request, 'plans/exercise_plan_detail.html', {'exercise_plan': exercise_plan})


def nutrition_plans(request):
    plans = NutritionPlan.objects.all()
    return render(request, 'plans/nutrition_plans.html', {'nutrition_plans': plans})


def nutrition_plan_detail(request, plan_id):
    nutrition_plan = get_object_or_404(NutritionPlan, id=plan_id)
    return render(request, 'plans/nutrition_plan_detail.html', {'nutrition_plan': nutrition_plan})

@login_required
@user_passes_test(is_admin)
def admin_edit_exercise_plan(request, plan_id):
    plan = get_object_or_404(ExercisePlan, id=plan_id)
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.description = request.POST.get('description')
        plan.price = request.POST.get('price')
        plan.duration = request.POST.get('duration')
        plan.save()
        messages.success(request, "Exercise plan updated successfully!")
        return redirect('admin_manage_exercise_plans')
    return render(request, 'admins/edit_exercise_plan.html', {'plan': plan})

@login_required
@user_passes_test(is_admin)
def admin_delete_exercise_plan(request, plan_id):
    plan = get_object_or_404(ExercisePlan, id=plan_id)
    plan.delete()
    messages.success(request, f"The exercise plan '{plan.name}' was deleted successfully.")
    return redirect('admin_manage_exercise_plans')

@login_required
@user_passes_test(is_admin)
def admin_edit_nutrition_plan(request, plan_id):
    plan = get_object_or_404(NutritionPlan, id=plan_id)
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.description = request.POST.get('description')
        plan.price = request.POST.get('price')
        plan.duration = request.POST.get('duration')
        plan.save()
        messages.success(request, "Nutrition plan updated successfully!")
        return redirect('admin_manage_nutrition_plans')
    return render(request, 'admins/edit_nutrition_plan.html', {'plan': plan})

@login_required
@user_passes_test(is_admin)
def admin_delete_nutrition_plan(request, plan_id):
    plan = get_object_or_404(NutritionPlan, id=plan_id)
    plan.delete()
    messages.success(request, f"The nutrition plan '{plan.name}' was deleted successfully.")
    return redirect('admin_manage_nutrition_plans')

# Cart views
def shop_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for item_id, item_data in cart.items():
        try:
            item_type = item_data['type']
            quantity = item_data['quantity']

            if item_type == 'product':
                product = Product.objects.get(id=item_id)
                cart_items.append({
                    'id': item_id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity,
                    'subtotal': product.price * quantity,
                    'type': 'product'
                })
                total_price += product.price * quantity
            elif item_type == 'exercise':
                exercise_plan = ExercisePlan.objects.get(id=item_id)
                cart_items.append({
                    'id': item_id,
                    'name': exercise_plan.name,
                    'price': exercise_plan.price,
                    'quantity': quantity,
                    'subtotal': exercise_plan.price * quantity,
                    'type': 'exercise'
                })
                total_price += exercise_plan.price * quantity
            elif item_type == 'nutrition':
                nutrition_plan = NutritionPlan.objects.get(id=item_id)
                cart_items.append({
                    'id': item_id,
                    'name': nutrition_plan.name,
                    'price': nutrition_plan.price,
                    'quantity': quantity,
                    'subtotal': nutrition_plan.price * quantity,
                    'type': 'nutrition'
                })
                total_price += nutrition_plan.price * quantity
        except Exception as e:
            print(f"Error processing cart item: {e}")
            continue

    return render(request, 'account/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def add_to_cart(request, item_type, item_id):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        if item_id in cart:
            cart[item_id]['quantity'] += quantity
        else:
            cart[item_id] = {'type': item_type, 'quantity': quantity}

        request.session['cart'] = cart
        messages.success(request, "Item successfully added to your cart!")
        return redirect('shop_cart')
    return redirect('shop_home')

# Function to remove an item from the cart
def remove_from_cart(request, item_id, item_type):
    cart = request.session.get('cart', {})

    if str(item_id) in cart:
        del cart[str(item_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart!")
    else:
        messages.error(request, "Item not found in cart.")

    return redirect('shop_cart')

# Order history and Payment views

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product', 'items__exercise_plan', 'items__nutrition_plan')
    return render(request, 'account/order_history.html', {'orders': orders})

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def checkout(request):
    # Extracting the user's cart
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # Processing basket items
    for item_id, details in cart.items():
        item_type = details.get('type')
        item_quantity = details.get('quantity')

        if item_type == 'product':
            product = Product.objects.get(id=item_id)
            subtotal = product.price * item_quantity
            cart_items.append({
                'name': product.name,
                'price': product.price,
                'quantity': item_quantity,
                'subtotal': subtotal,
            })
            total_price += subtotal
        elif item_type == 'exercise':
            plan = ExercisePlan.objects.get(id=item_id)
            subtotal = plan.price * item_quantity
            cart_items.append({
                'name': plan.name,
                'price': plan.price,
                'quantity': item_quantity,
                'subtotal': subtotal,
            })
            total_price += subtotal
        elif item_type == 'nutrition':
            plan = NutritionPlan.objects.get(id=item_id)
            subtotal = plan.price * item_quantity
            cart_items.append({
                'name': plan.name,
                'price': plan.price,
                'quantity': item_quantity,
                'subtotal': subtotal,
            })
            total_price += subtotal

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY,
    }

    return render(request, 'shop/checkout.html', context)


@csrf_exempt
def stripe_checkout(request):
    if request.method == "POST":
        return JsonResponse({"client_secret": "mock_client_secret"})

    return JsonResponse({"error": "Invalid request method"}, status=400)

def calculate_order_total(request):
    cart = request.session.get('cart', {})
    total = 0
    for item in cart:
        total += item['price'] * item['quantity']
    return int(total * 100)

@login_required
def payment_success(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop_home')

    order = Order.objects.create(
        user=request.user,
        total_price=0,
        is_paid=True
    )

    # Add items to the order

    for item_id, item_data in cart.items():
        quantity = item_data.get('quantity', 1)
        if item_data['type'] == 'product':
            product = Product.objects.get(id=item_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        elif item_data['type'] == 'exercise_plan':
            plan = ExercisePlan.objects.get(id=item_id)
            OrderItem.objects.create(order=order, exercise_plan=plan, quantity=quantity)
        elif item_data['type'] == 'nutrition_plan':
            plan = NutritionPlan.objects.get(id=item_id)
            OrderItem.objects.create(order=order, nutrition_plan=plan, quantity=quantity)
    # Total price
    order.calculate_total_price()

# Clear cart
    request.session['cart'] = {}
    return render(request, 'shop/payment_success.html', {'order': order})

# Stripe
def checkout_view(request):
    context = {
        "stripe_public_key": settings.STRIPE_TEST_PUBLIC_KEY,
    }
    return render(request, "shop/checkout.html", context)

# Support Requests
@login_required
@user_passes_test(is_admin)
def admin_support_requests(request):
    if request.method == "POST":
        support_id = request.POST.get("support_id")
        action = request.POST.get("action")

        try:
            support_request = get_object_or_404(SupportRequest, id=support_id)

            if action == "delete":
                support_request.delete()
                messages.success(request, "Support request deleted successfully.")
            elif action == "in_review":
                support_request.status = "in_review"
                support_request.save()
                messages.success(request, "Support request marked as 'In Review'.")
            elif action == "done":
                support_request.status = "done"
                support_request.save()
                messages.success(request, "Support request marked as 'Done'.")
            elif action == "rejected":
                support_request.status = "rejected"
                support_request.save()
                messages.success(request, "Support request rejected.")
            else:
                messages.error(request, "Unknown action.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    support_requests = SupportRequest.objects.all()
    return render(request, "admins/support_requests.html", {"requests": support_requests})

# Support Request Page
def support_view(request):
    return render(request, 'main/support.html')

# Submit Support Request
def submit_support_request(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        request_type = request.POST.get("request_type")
        message = request.POST.get("message")

        if name and email and request_type and message:
            SupportRequest.objects.create(
                name=name,
                email=email,
                request_type=request_type,
                message=message
            )
            messages.success(request, "Your support request has been submitted successfully.")
        else:
            messages.error(request, "All fields are required.")

        return redirect("support")

    return redirect("support")

# Custom 404
def custom_404(request, exception):
    return render(request, 'error/404.html', status=404)