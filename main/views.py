from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User, Group, Permission
from main.forms import LoginForm, SignUpForm, UserProfileForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from main.models import UserProfile


def home(request):
    is_admin = request.user.groups.filter(name='Admin').exists() if request.user.is_authenticated else False
    return render(request, 'main/home.html', {'is_admin': is_admin})


def about(request):
    return render(request, 'main/about_us.html')


def support(request):
    default_type = request.GET.get('type', 'technical')
    return render(request, 'main/support.html', {'default_type': default_type})


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


# Admin Panel Views
def is_admin(user):
    return user.groups.filter(name='Admin').exists()


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
