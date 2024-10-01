from django.urls import path
from users import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('plans/', views.plans_view, name='plans'),
    path('shop/', views.shop_view, name='shop'),
    path('about/', views.about_view, name='about'),
    path('support/', views.support_view, name='support'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:plan_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('profile/', views.profile_view, name='profile'),
    path('all-posts/', views.all_posts_view, name='all_posts'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # Admin Dashboard route
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
