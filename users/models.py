from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

# Automatically assign user roles when a new user is created
@receiver(post_save, sender=User)
def assign_user_role(sender, instance, created, **kwargs):
    if created:
        if instance.id == 1:
            admin_group, _ = Group.objects.get_or_create(name='Administrator')
            instance.groups.add(admin_group)
        else:
            user_group, _ = Group.objects.get_or_create(name='User')
            instance.groups.add(user_group)

        instance.save()

# Model for user posts (updates)
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

# Model for Exercise and Nutrition Plans
class Plan(models.Model):
    PLAN_TYPES = [
        ('workout', 'Workout Plan'),
        ('nutrition', 'Nutrition Plan'),
    ]
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Model for the shopping cart
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)  # Plan model reference
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.plan.title} ({self.quantity}) for {self.user.username}"

    def get_total_price(self):
        return self.plan.price * self.quantity  # Calculate total price for the cart item

# Model for orders
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
