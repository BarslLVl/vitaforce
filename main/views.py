from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group
from main.forms import LoginForm, SignUpForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.models import UserProfile

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
            return redirect('my_profile')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Sign-up view
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='User')  # Default group
            user.groups.add(group)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'auth/signup.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')

# Profile view
@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    user_group = user.groups.first()
    group_name = user_group.name if user_group else "User"
    return render(request, 'account/my_profile.html', {
        'user': user,
        'profile': profile,
        'group_name': group_name
    })

# Settings view
@login_required
def settings_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

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

# Update Email
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

# Change Password
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

# Update Personal Information
@login_required
def update_personal_info(request):
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your personal information has been updated successfully.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    return redirect('settings')