from django import forms
from .models import Post
from .models import Plan

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Share your progress...'}),
        } # Post form fields

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'description', 'price', 'plan_type'] #Form fields