"""
Forms for the ride-sharing application.
Includes forms for user registration, profile management, and ride operations.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Transaction

class SignUpForm(UserCreationForm):
    """
    Extended user registration form with location field.
    Customizes form fields with Bootstrap classes and creates UserProfile on save.
    """
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city (e.g., London)',
                'required': 'required'
            }
        )
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'location', 'password1', 'password2')

    def save(self, commit=True):
        """
        Overrides save method to:
        1. Save the User instance
        2. Create associated UserProfile with location
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile with location
            UserProfile.objects.create(
                user=user,
                location=self.cleaned_data['location']
            )
        return user

class UserRegistrationForm(UserCreationForm):
    """
    Basic user registration form with email validation.
    Used as an alternative to SignUpForm in some views.
    """
    email = forms.EmailField()

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    """
    Form for basic user profile updates.
    Makes all fields optional by default.
    """
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        """Initialize form with all fields set to not required"""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class DriverApplicationForm(forms.ModelForm):
    """
    Form for driver applications.
    Requires license file upload and car model information.
    """
    class Meta:
        model = UserProfile
        fields = ['license_file', 'car_model']
        widgets = {
            'license_file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_phone_number(self):
        """Validate that phone number is provided for drivers"""
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError("Phone number is required for drivers")
        return phone

class ProfileUpdateForm(forms.ModelForm):
    """
    Comprehensive profile update form with:
    - Profile picture upload
    - Location update
    - Bio/description field
    """
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'  # Restrict to image files
        })
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city (e.g., London)'
        })
    )
    bio = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Tell us about yourself...'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'location', 'bio']

class RideCreateForm(forms.ModelForm):
    """
    Form for drivers to create new ride offers.
    Includes validation for monetary amounts.
    """
    class Meta:
        model = Transaction
        fields = ['pickup_location', 'dropoff_location', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'})  # Decimal precision
        }

class RideSearchForm(forms.Form):
    """
    Form for searching available rides.
    Basic form with pickup and dropoff location fields.
    """
    pickup_location = forms.CharField(max_length=200)
    dropoff_location = forms.CharField(max_length=200)
