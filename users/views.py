from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Custom authentication function that allows login with email or username
def custom_authenticate(username_or_email, password):
    try:
        # Check if the input is an email or a username
        user = User.objects.get(email=username_or_email)
        username = user.username  # Get the username if an email was provided
    except User.DoesNotExist:
        # If no email is found, treat the input as a username
        username = username_or_email

    # Authenticate using username and password
    user = authenticate(username=username, password=password)
    return user

# Login View
def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST['email_or_username']
        password = request.POST['password']
        
        # Use the custom authentication function
        user = custom_authenticate(username_or_email, password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the homepage after login
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

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        # Create new user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Log the user in after successful registration
        login(request, user)
        return redirect('home')

    return render(request, 'user/signup.html')

# Support
from django.shortcuts import render

def support_view(request):
    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        

        return render(request, 'user/support_success.html', {'name': full_name})
    return render(request, 'user/support.html')

# Cart
def cart_view(request):
    return render(request, 'purse/cart.html')

# View for the homepage
def index(request):
    return render(request, 'user/index.html')

# View for the Plans Page
def plans_view(request):
    return render(request, 'user/plans.html')

# View for the Shop Page
def shop_view(request):
    return render(request, 'user/shop.html')

# View for the About Page
def about_view(request):
    return render(request, 'user/about.html')