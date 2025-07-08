from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # Add other fields as needed, e.g., birth_date, location, etc.

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create or update the user profile whenever a User instance is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Ensure profile exists, create if it somehow got deleted
        UserProfile.objects.get_or_create(user=instance)
        # If you want to update profile fields based on user fields, do it here.
        # For example: instance.profile.some_field = instance.some_user_field
    instance.profile.save()
