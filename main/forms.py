# main/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Transaction

class SignUpForm(UserCreationForm):
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
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create UserProfile
            from .models import UserProfile
            UserProfile.objects.create(
                user=user,
                location=self.cleaned_data['location']
            )
        return user

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class DriverApplicationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['license_file', 'car_model']
        widgets = {
            'license_file': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            raise forms.ValidationError("Phone number is required for drivers")
        return phone

class ProfileUpdateForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
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
    class Meta:
        model = Transaction
        fields = ['pickup_location', 'dropoff_location', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'})
        }

class RideSearchForm(forms.Form):
    pickup_location = forms.CharField(max_length=200)
    dropoff_location = forms.CharField(max_length=200)