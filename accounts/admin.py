from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile # Make sure UserProfile is imported

# Define an inline admin descriptor for UserProfile model
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('bio', 'profile_picture') # Specify fields to show, add more if UserProfile gets more fields

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    # To make profile fields available for list_display or other admin features if needed:
    # def get_bio(self, instance):
    #     return instance.profile.bio
    # get_bio.short_description = 'Bio'
    #
    # # Add 'get_bio' to list_display if you want it there:
    # list_display = ('username', 'email', 'first_name', 'last_name', 'get_bio', 'is_active', 'is_staff')


# Re-register UserAdmin (User is already registered by Django by default)
# It's better to unregister first, then register with the custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
