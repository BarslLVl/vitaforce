from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from tinymce.models import HTMLField


# User Profile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Category model for Products
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# Signal for generating slug
@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


# Product model
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock > 0

    def stock_status(self):
        return "In Stock" if self.is_in_stock() else "Out of Stock"


# Exercise Plan model
class ExercisePlan(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


# Nutrition Plan model
class NutritionPlan(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


# Order model for storing user orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_price = total
        self.save()


# OrderItem model for tracking items in an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    exercise_plan = models.ForeignKey(ExercisePlan, on_delete=models.CASCADE, blank=True, null=True)
    nutrition_plan = models.ForeignKey(NutritionPlan, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name}"
        elif self.exercise_plan:
            return f"{self.quantity} x {self.exercise_plan.name}"
        elif self.nutrition_plan:
            return f"{self.quantity} x {self.nutrition_plan.name}"
        return "OrderItem"

    def get_subtotal(self):
        if self.product:
            return self.product.price * self.quantity
        elif self.exercise_plan:
            return self.exercise_plan.price * self.quantity
        elif self.nutrition_plan:
            return self.nutrition_plan.price * self.quantity
        return 0


# Support Request model
class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('not_reviewed', 'Not Reviewed'),
        ('in_review', 'In Review'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    request_type = models.CharField(max_length=50)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_reviewed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.request_type}"
    
# Review/Posts
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
