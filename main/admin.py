from django.contrib import admin
from main.models import UserProfile

# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'date_of_birth')
    search_fields = ('user__username', 'first_name', 'last_name')