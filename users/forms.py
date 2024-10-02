from django import forms
from django.contrib.auth.models import User
from .models import Post, Plan, Product

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Share your progress...'}),
        }

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'description', 'price', 'plan_type']
        labels = {
            'plan_type': 'Type of Plan',
        }

# ProductForm for the Product model
class ProductForm(forms.ModelForm):
    PRODUCT_CATEGORIES = [
        ('nutrition', 'Nutrition'),
        ('exercise', 'Exercise'),
    ]
    
    category = forms.ChoiceField(choices=PRODUCT_CATEGORIES, label="Category")

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'image']
        labels = {
            'name': 'Product Name',
            'description': 'Product Description',
            'price': 'Price',
            'category': 'Category',
            'image': 'Product Image',
        }

# Edit user form for User model including password change
class UserEditForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
