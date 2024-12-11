from django.contrib import admin
from main.models import UserProfile, Category, Product, ExercisePlan, NutritionPlan, Order, OrderItem, SupportRequest

# Admin for UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'date_of_birth', 'email')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')

# Admin for Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

# Admin for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_in_stock', 'image_display')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    fields = ('name', 'category', 'description', 'price', 'stock', 'image')

    def image_display(self, obj):
        if obj.image:
            return f"<img src='{obj.image.url}' width='50' height='50' style='object-fit:cover;'/>"
        return "No Image"
    image_display.allow_tags = True
    image_display.short_description = "Image Preview"

# Admin for Exercise Plans
@admin.register(ExercisePlan)
class ExercisePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'price', 'duration')

# Admin for Nutrition Plans
@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name', 'description')
    fields = ('name', 'description', 'price', 'duration')

# Admin for Orders
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price', 'is_paid')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]

# Admin for Order Items
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'exercise_plan', 'nutrition_plan', 'quantity', 'get_subtotal')
    list_filter = ('order',)

    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = "Subtotal"
    

# Support Registration
@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'request_type', 'created_at')
    search_fields = ('name', 'email', 'request_type')
    list_filter = ('request_type', 'created_at')
