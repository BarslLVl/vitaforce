"""
URL configuration for vitaforce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from main.views import (
    login_view, signup_view, logout_view, profile_view, settings_view,
    update_email, update_personal_info, change_password, home, about, support
)

urlpatterns = [
    path('', home, name='home'),
    path('about_us/', about, name='about_us'),
    path('support/', support, name='support'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='my_profile'),
    path('settings/', settings_view, name='settings'),
    path('settings/update-personal-info/', update_personal_info, name='update_personal_info'),
    path('settings/update-email/', update_email, name='update_email'),
    path('settings/change-password/', change_password, name='change_password'),
]
