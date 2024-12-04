from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm

# Home page view
def home(request):
    return render(request, 'main/home.html')

# About page view
def about(request):
    return render(request, 'main/about_us.html')

# Support page view
def support(request):
    default_type = request.GET.get('type', 'technical')
    return render(request, 'main/support.html', {'default_type': default_type})



# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Sign-up view
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('home')
