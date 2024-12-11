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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views
from django.conf.urls import handler404

urlpatterns = [
    # Tinymce editor
    path('tinymce/', include('tinymce.urls')),
    
    # General pages
    path('', views.home, name='home'),
    path('favicon.ico', views.favicon, name='favicon'),
    path('about_us/', views.about, name='about_us'),
    path("support/", views.support_view, name="support"),
    path("support/submit/", views.submit_support_request, name="submit_support_request"),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('reviews/all/', views.all_reviews, name='all_reviews'),
    path('posts/all/', views.all_posts, name='all_posts'),
    
    # User pages
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='my_profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/update-personal-info/', views.update_personal_info, name='update_personal_info'),
    path('settings/update-email/', views.update_email, name='update_email'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('reviews/my/', views.my_reviews, name='my_reviews'),
    path('reviews/new/', views.create_review, name='create_review'),
    path('reviews/edit/<int:pk>/', views.edit_review, name='edit_review'),
    path('reviews/delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('posts/my/', views.my_posts, name='my_posts'),
    path('posts/new/', views.create_post, name='create_post'),
    path('posts/edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('posts/delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('my-content/', views.my_content, name='my_content'),

    # Admin panel
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/users/', views.admin_manage_users, name='admin_manage_users'),
    path('admin-panel/groups/', views.admin_manage_groups, name='admin_manage_groups'),
    path('admin-panel/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-panel/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/groups/edit/<int:group_id>/', views.admin_edit_group, name='admin_edit_group'),
    path('admin-panel/groups/delete/<int:group_id>/', views.admin_delete_group, name='admin_delete_group'),
    path('admin-panel/categories/', views.admin_manage_categories, name='admin_manage_categories'),
    path('admin-panel/categories/edit/<int:category_id>/', views.admin_edit_category, name='admin_edit_category'),
    path('admin-panel/categories/delete/<int:category_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('admin-panel/products/', views.admin_manage_products, name='admin_manage_products'),
    path('admin-panel/products/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin-panel/products/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('admin-panel/exercise-plans/', views.admin_manage_exercise_plans, name='admin_manage_exercise_plans'),
    path('admin-panel/nutrition-plans/', views.admin_manage_nutrition_plans, name='admin_manage_nutrition_plans'),
    path('admin-panel/exercise-plans/edit/<int:plan_id>/', views.admin_edit_exercise_plan, name='admin_edit_exercise_plan'),
    path('admin-panel/exercise-plans/delete/<int:plan_id>/', views.admin_delete_exercise_plan, name='admin_delete_exercise_plan'),
    path('admin-panel/nutrition-plans/edit/<int:plan_id>/', views.admin_edit_nutrition_plan, name='admin_edit_nutrition_plan'),
    path('admin-panel/nutrition-plans/delete/<int:plan_id>/', views.admin_delete_nutrition_plan, name='admin_delete_nutrition_plan'),
    path('admin-panel/support-requests/', views.admin_support_requests, name='admin_support_requests'),
    path("admin/support-requests/", views.admin_support_requests, name="admin_support_requests"),
    path('admin-panel/manage-posts/', views.admin_manage_posts, name='admin_manage_posts'),
    path('admin-panel/manage-reviews/', views.admin_manage_reviews, name='admin_manage_reviews'),
    path('admin-panel/edit-post/<int:pk>/', views.admin_edit_post, name='admin_edit_post'),
    path('admin-panel/delete-post/<int:pk>/', views.admin_delete_post, name='admin_delete_post'),
    path('admin-panel/edit-review/<int:pk>/', views.admin_edit_review, name='admin_edit_review'),
    path('admin-panel/delete-review/<int:pk>/', views.admin_delete_review, name='admin_delete_review'),


    # Shop pages
    path('shop/', views.shop_home, name='shop_home'),
    path('shop/category/<slug:slug>/', views.shop_category, name='shop_category'),
    path('shop/product/<int:product_id>/', views.shop_product_detail, name='shop_product_detail'),
    path('shop/cart/', views.shop_cart, name='shop_cart'),
    path('shop/checkout/', views.checkout, name='checkout'),

    # Plans pages
    path('plans/exercise/', views.exercise_plans, name='exercise_plans'),
    path('plans/exercise/<int:plan_id>/', views.exercise_plan_detail, name='exercise_plan_detail'),
    path('plans/nutrition/', views.nutrition_plans, name='nutrition_plans'),
    path('plans/nutrition/<int:plan_id>/', views.nutrition_plan_detail, name='shop_nutrition_plan_detail'),

    # Cart/Pay/Order History
    path('shop/cart/', views.shop_cart, name='shop_cart'),
    path('shop/add-to-cart/<str:item_type>/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('shop/cart/remove/<int:item_id>/<str:item_type>/', views.remove_from_cart, name='remove_from_cart'),
    path('shop/checkout/', views.checkout, name='checkout'),
    path("checkout/", views.stripe_checkout, name="stripe_checkout"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path('shop/order-history/', views.order_history, name='order_history'),
    path('stripe/checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('shop/checkout/stripe/', views.stripe_checkout, name='stripe_checkout'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'main.views.custom_404'