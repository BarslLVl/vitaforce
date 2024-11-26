from django.contrib import admin
from django.urls import path
from users import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import TemplateView
from users.views import admin_roles
from users.views import payment_failure_view

from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, 'error/404.html', status=404)

handler404 = custom_404

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
    path('checkout/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment-failure/', payment_failure_view, name='payment_failure'),
    path('add-to-cart/product/<int:product_id>/', views.add_to_cart_product, name='add_to_cart_product'),

    # Admin Dashboard routes
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/plans/', views.admin_plans, name='admin_plans'),
    path('admin/create_plan/', views.create_plan, name='create_plan'),
    path('admin/plans/edit/<int:plan_id>/', views.edit_plan, name='edit_plan'),
    path('admin/plans/delete/<int:plan_id>/', views.delete_plan, name='delete_plan'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/create_product/', views.create_product, name='create_product'),
    path('admin/edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin/delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('admin/roles/', admin_roles, name='admin_roles'),
    

    # Django Admin
    path('admin/', admin.site.urls),
    
    # Account pages routes
    path('account/', views.account_view, name='account'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/purchases/', views.account_purchases, name='account_purchases'),
    path('account/posts/', views.account_posts, name='account_posts'),
    path('account/posts/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('account/posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Sitemap: /sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

from users.views import CreateCheckoutSessionView

urlpatterns += [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]
    