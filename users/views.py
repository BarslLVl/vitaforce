import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Post, Plan, CartItem, Order
from .forms import PostForm

# Stripe API ключи
stripe.api_key = settings.STRIPE_SECRET_KEY

# Custom authentication function that allows login with email or username
def custom_authenticate(username_or_email, password):
    try:
        user = User.objects.get(email=username_or_email)
        username = user.username
    except User.DoesNotExist:
        username = username_or_email

    user = authenticate(username=username, password=password)
    return user

# Login View
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

# Sign Up View
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

# User Profile View
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

# Add to Cart View
@login_required
def add_to_cart(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, plan=plan)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

# Remove from Cart View
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

# Cart View
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum([item.get_total_price() for item in cart_items])
    return render(request, 'purse/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Stripe Checkout View
@login_required
def checkout(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    if request.method == "POST":
        # Create a Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(plan.price * 100),  # Сумма в центах
            currency='gbp',
            payment_method_types=['card'],
            metadata={'plan_id': plan.id}
        )

        # Create a new order with the stripe payment intent ID
        order = Order.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price,
            stripe_payment_intent=intent['id']
        )

        return render(request, 'purse/checkout.html', {
            'client_secret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            'plan': plan
        })

    return render(request, 'purse/checkout.html', {'plan': plan})

# Payment Success View
@login_required
def payment_success(request):
    return render(request, 'purse/payment_success.html')

# Index (Homepage) View
def index(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    
    is_admin = False
    if request.user.is_authenticated and request.user.groups.filter(name='Administrator').exists():
        is_admin = True

    return render(request, 'user/index.html', {
        'latest_posts': latest_posts,
        'is_admin': is_admin
    })

# All Posts View
def all_posts_view(request):
    all_posts = Post.objects.all().order_by('-created_at')
    return render(request, 'user/all_posts.html', {'all_posts': all_posts})

# Plans View
def plans_view(request):
    plans = Plan.objects.all()
    return render(request, 'user/plans.html', {'plans': plans})

# Support View
def support_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        return render(request, 'user/support_success.html', {'name': full_name})
    return render(request, 'user/support.html')

# Shop View
def shop_view(request):
    return render(request, 'user/shop.html')

# About View
def about_view(request):
    return render(request, 'user/about.html')

# Admin Dashboard View
@login_required
def admin_dashboard(request):
    if not request.user.groups.filter(name='Administrator').exists():
        return redirect('home')

    return render(request, 'admin/admin_dashboard.html')
