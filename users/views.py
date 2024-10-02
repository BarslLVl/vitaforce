import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import Post, Plan, CartItem, Order, Product
from .forms import PostForm, PlanForm, ProductForm, UserEditForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def custom_authenticate(username_or_email, password):
    try:
        user = User.objects.get(email=username_or_email)
        username = user.username
    except User.DoesNotExist:
        username = username_or_email

    user = authenticate(username=username, password=password)
    return user

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST['email_or_username']
        password = request.POST['password']

        user = custom_authenticate(username_or_email, password)

        if user is not None:
            if user.groups.filter(name='Banned').exists():
                messages.error(request, "Your account has been banned by the site administrator.")
                return redirect('login')
            else:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, "Invalid email/username or password.")
    
    return render(request, 'user/login.html')

def signup_view(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        if User.objects.count() == 1:
            admin_group, _ = Group.objects.get_or_create(name='Administrator')
            user.groups.add(admin_group)
        else:
            user_group, _ = Group.objects.get_or_create(name='User')
            user.groups.add(user_group)
        
        user.save()
        login(request, user)
        return redirect('home')

    return render(request, 'user/signup.html')

@login_required
def profile_view(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('profile')
    else:
        form = PostForm()

    return render(request, 'user/profile.html', {'posts': posts, 'form': form})

@login_required
def add_to_cart(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, plan=plan)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def add_to_cart_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum([item.get_total_price() for item in cart_items])
    return render(request, 'purse/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum([item.get_total_price() for item in cart_items])

    if request.method == "POST":
        intent = stripe.PaymentIntent.create(
            amount=int(total_price * 100),
            currency='gbp',
            payment_method_types=['card'],
        )

        return render(request, 'purse/checkout.html', {
            'client_secret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'cart_items': cart_items,
            'total_price': total_price
        })

    return render(request, 'purse/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def payment_success_view(request):
    return render(request, 'purse/payment_success.html')

@login_required
def payment_failure_view(request):
    return render(request, 'purse/payment_failure.html')

def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    
    is_admin = False
    if request.user.is_authenticated and request.user.groups.filter(name='Administrator').exists():
        is_admin = True

    return render(request, 'user/index.html', {
        'latest_posts': latest_posts,
        'is_admin': is_admin
    })

def all_posts_view(request):
    all_posts = Post.objects.all().order_by('-created_at')
    return render(request, 'user/all_posts.html', {'all_posts': all_posts})

def plans_view(request):
    plans = Plan.objects.all()
    return render(request, 'user/plans.html', {'plans': plans})

def support_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        return render(request, 'user/support_success.html', {'name': full_name})
    return render(request, 'user/support.html')

def shop_view(request):
    products = Product.objects.all()
    return render(request, 'user/shop.html', {'products': products})

def about_view(request):
    return render(request, 'user/about.html')

@login_required
def admin_dashboard(request):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    return render(request, 'admin/admin_dashboard.html')

@login_required
def admin_plans(request):
    plans = Plan.objects.all()
    return render(request, 'admin/admin_plans.html', {'plans': plans})

@login_required
def admin_products(request):
    products = Product.objects.all()
    return render(request, 'admin/admin_products.html', {'products': products})

@login_required
def admin_users(request):
    users = User.objects.all()
    return render(request, 'admin/admin_users.html', {'users': users})

@login_required
def create_plan(request):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_plans')
    else:
        form = PlanForm()

    return render(request, 'admin/create_plan.html', {'form': form})

@login_required
def edit_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('admin_plans')
    else:
        form = PlanForm(instance=plan)

    return render(request, 'admin/edit_plan.html', {'form': form, 'plan': plan})

@login_required
def delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        plan.delete()
        return redirect('admin_plans')

    return render(request, 'admin/delete_plan.html', {'plan': plan})

@login_required
def create_product(request):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_products')
    else:
        form = ProductForm()

    return render(request, 'admin/create_product.html', {'form': form})

@login_required
def edit_user(request, user_id):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)

        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            user.save()
            messages.success(request, "User details updated successfully.")
            return redirect('admin_users')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'admin/edit_user.html', {'form': form, 'user': user})

@login_required
def edit_product(request, product_id):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('admin_products')

@login_required
def account_view(request):
    return render(request, 'profile/account.html', {'user': request.user})

@login_required
def account_settings(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            user.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('account_settings')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'profile/account_settings.html', {'form': form})

@login_required
def account_purchases(request):
    orders = Order.objects.filter(user=request.user)
    plans = Plan.objects.filter(cartitem__user=request.user)
    return render(request, 'profile/account_purchases.html', {'orders': orders, 'plans': plans})

# My Posts View (List and Create New Post)
@login_required
def account_posts(request):
    posts = Post.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            messages.success(request, "Post created successfully.")
            return redirect('account_posts')
    else:
        form = PostForm()

    return render(request, 'profile/account_posts.html', {'posts': posts, 'form': form})

# Edit Post View
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect('account_posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'profile/edit_post.html', {'form': form})

# Delete Post View
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('account_posts')

    return render(request, 'profile/delete_post.html', {'post': post})

def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'user/index.html', {'latest_posts': latest_posts})