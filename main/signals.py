"""
Signal handlers for the main application.
These signals automatically create and manage UserProfile instances
whenever User instances are created or updated.
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a UserProfile whenever a new User is created.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional arguments
        
    Behavior:
        - Only triggers when a User is first created (created=True)
        - Creates a UserProfile with default driver settings
        - Uses get_or_create to prevent duplicates
    """
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'is_driver': False,          # Default to non-driver status
                'has_valid_license': False,  # Default to no valid license
            }
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal receiver that ensures a UserProfile exists and is saved
    whenever a User is saved.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being saved
        **kwargs: Additional arguments
        
    Behavior:
        - Checks if UserProfile exists
        - Creates one with defaults if missing
        - Saves existing profile
        - Gracefully handles exceptions with error logging
        
    Note:
        This serves as a failsafe in case create_user_profile doesn't execute
    """
    try:
        if not hasattr(instance, 'userprofile'):
            # Create new profile if one doesn't exist
            UserProfile.objects.create(
                user=instance,
                is_driver=False,
                has_valid_license=False,
            )
        else:
            # Save existing profile
            instance.userprofile.save()
    except Exception as e:
        # Basic error handling - in production should use proper logging
        print(f"Error saving user profile: {e}")
        # Consider adding: logger.error(f"Error saving user profile: {e}")
