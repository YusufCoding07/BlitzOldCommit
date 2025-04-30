# Import required Django modules and libraries
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.utils import timezone
from decimal import Decimal

class UserProfile(models.Model):
    """
    Extended user profile model that stores additional information about users.
    Includes driver-specific fields for ride-sharing functionality.
    """
    
    # One-to-one relationship with Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Basic profile information
    location = models.CharField(max_length=200, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    
    # Driver-related fields
    is_driver = models.BooleanField(default=False)
    has_valid_license = models.BooleanField(default=False)
    car_model = models.CharField(max_length=100, default='')
    
    # Profile picture with default upload path
    profile_picture = models.ImageField(upload_to='profile_pics/', default='', blank=True)
    
    # Timestamps for record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Driver application status with predefined choices
    driver_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    # Driver application documents
    license_file = models.FileField(upload_to='driver_documents/', null=True, blank=True)
    application_date = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        """String representation of the user profile"""
        return f"{self.user.username}'s profile"

class Transaction(models.Model):
    """
    Financial transaction model for tracking payments and earnings
    related to ride-sharing services.
    """
    
    # Transaction type choices
    TRANSACTION_TYPES = [
        ('ride', 'Ride Posting'),
        ('payment', 'Payment'),
        ('earning', 'Earning'),
    ]
    
    # Status choices for transactions
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # User who initiated the transaction
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Driver associated with the transaction (optional)
    driver = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='driven_transactions'
    )
    
    # Transaction amount with decimal precision
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Current status of the transaction
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Type of transaction
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES, 
        default='ride'
    )
    
    # Location information
    pickup_location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=200)
    
    # Additional details
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata options including default ordering"""
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the transaction"""
        return f"{self.user.username}'s {self.transaction_type} - {self.amount}"

# Signal receivers to automatically create/save user profiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a UserProfile whenever a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal receiver that ensures a UserProfile exists and is saved
    whenever a User is saved.
    """
    try:
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance)
        instance.userprofile.save()
    except Exception as e:
        print(f"Error saving user profile: {e}")

class Ride(models.Model):
    """
    Model representing ride offers in the ride-sharing system.
    """
    
    # Status choices for rides
    RIDE_STATUS_CHOICES = [
        ('open', 'Open'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    # Driver offering the ride
    driver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='rides_offered'
    )
    
    # Ride location details
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    
    # Ride timing
    date = models.DateField()
    time = models.TimeField()
    
    # Pricing and capacity
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seats_available = models.IntegerField(default=1)
    
    # Current status
    status = models.CharField(
        max_length=20, 
        choices=RIDE_STATUS_CHOICES, 
        default='open'
    )
    
    # Creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Metadata options including default ordering"""
        ordering = ['date', 'time']

    def __str__(self):
        """String representation of the ride"""
        return f"Ride from {self.pickup_location} to {self.dropoff_location} on {self.date}"
