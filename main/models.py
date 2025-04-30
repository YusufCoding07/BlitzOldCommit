from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils import timezone
from decimal import Decimal

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=200, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_driver = models.BooleanField(default=False)
    has_valid_license = models.BooleanField(default=False)
    car_model = models.CharField(max_length=100, default='')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Driver application fields
    driver_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    license_file = models.FileField(upload_to='driver_documents/', null=True, blank=True)
    application_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('ride', 'Ride Posting'),
        ('payment', 'Payment'),
        ('earning', 'Earning'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driven_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='ride')
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.transaction_type} - {self.amount}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        instance.userprofile.save()
    except Exception as e:
        print(f"Error saving user profile: {e}")

class Ride(models.Model):
    RIDE_STATUS_CHOICES = [
        ('open', 'Open'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_offered')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seats_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=RIDE_STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location} on {self.date}"