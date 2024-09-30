from django.urls import path
from users import views  # Adjust the path based on where your views.py file is located

urlpatterns = [
    path('', views.index, name='home'),  # Home page
    path('login/', views.login_view, name='login'),  # Login page
    path('signup/', views.signup_view, name='signup'),  # Signup page
    path('plans/', views.plans_view, name='plans'),  # New route for Plans page
    path('shop/', views.shop_view, name='shop'),  # New route for Shop page
    path('about/', views.about_view, name='about'),  # New route for About page
    path('support/', views.support_view, name='support'),  # New route for Support page
    path('cart/', views.cart_view, name='cart'),  # New route for Cart page
]
