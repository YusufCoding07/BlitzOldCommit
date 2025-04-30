# main/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'is_driver': False,
                'has_valid_license': False,
            }
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(
                user=instance,
                is_driver=False,
                has_valid_license=False,
            )
        else:
            instance.userprofile.save()
    except Exception as e:
        print(f"Error saving user profile: {e}")