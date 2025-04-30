"""
Main application views for the ride-sharing platform.
Handles user authentication, profile management, ride operations, and transactions.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Transaction, UserProfile, Ride
from .forms import UserProfileForm, DriverApplicationForm, UserRegistrationForm, RideCreateForm, RideSearchForm, SignUpForm, ProfileUpdateForm
import logging
import traceback
from django.utils import timezone
from django.db.models import Q, Sum, Avg
from django import forms
from django.db import transaction
from decimal import Decimal
from datetime import datetime

# Initialize logger
logger = logging.getLogger('django')

def home(request):
    """
    Home page view showing nearby rides for authenticated users.
    For unauthenticated users, shows basic landing page.
    """
    nearby_rides = []
    
    if request.user.is_authenticated:
        user_location = request.user.userprofile.location
        # Get rides matching user's location or nearby areas
        nearby_rides = Transaction.objects.filter(
            Q(status='pending') &
            (Q(pickup_location__icontains=user_location) |
             Q(dropoff_location__icontains=user_location))
        ).order_by('-created_at')[:5]  # Show 5 most recent nearby rides
    
    context = {
        'nearby_rides': nearby_rides
    }
    return render(request, 'main/home.html', context)

@login_required
def profile(request):
    """
    User profile view showing:
    - Profile information
    - Transaction statistics
    - Recent transactions
    - Profile update form
    """
    # Get all transactions for this user
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate statistics
    earnings = transactions.filter(amount__gt=0)
    spendings = transactions.filter(amount__lt=0)
    
    # Calculate totals (handle None cases)
    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spendings = spendings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate averages (handle None cases)
    avg_earnings = earnings.aggregate(Avg('amount'))['amount__avg'] or 0
    avg_spendings = spendings.aggregate(Avg('amount'))['amount__avg'] or 0
    
    stats = {
        'total_earnings': abs(total_earnings),
        'total_spendings': abs(total_spendings),
        'avg_earnings': abs(avg_earnings),
        'avg_spendings': abs(avg_spendings),
        'has_earnings': earnings.exists(),
        'has_spendings': spendings.exists(),
    }

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.userprofile)
    
    return render(request, 'main/profile.html', {
        'form': form,
        'user': request.user,
        'transactions': transactions.order_by('-created_at')[:5],  # Show only last 5 transactions
        'stats': stats,
    })

def map_view(request):
    """Simple view rendering the map page"""
    return render(request, 'main/map.html')

@login_required
def transactions(request):
    """
    Transaction history view with filtering capabilities.
    Shows earnings, spendings, and transaction statistics.
    """
    transaction_type = request.GET.get('type', 'all')
    
    # Base query
    transactions = Transaction.objects.filter(user=request.user)
    
    # Calculate statistics
    earnings = transactions.filter(amount__gt=0)
    spendings = transactions.filter(amount__lt=0)
    
    # Calculate totals (handle None cases)
    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    total_spendings = spendings.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate averages (handle None cases)
    avg_earnings = earnings.aggregate(Avg('amount'))['amount__avg'] or 0
    avg_spendings = spendings.aggregate(Avg('amount'))['amount__avg'] or 0
    
    stats = {
        'total_earnings': abs(total_earnings),
        'total_spendings': abs(total_spendings),
        'avg_earnings': abs(avg_earnings),
        'avg_spendings': abs(avg_spendings),
    }
    
    # Filter based on type
    if transaction_type == 'earnings':
        transactions = earnings
    elif transaction_type == 'spendings':
        transactions = spendings
    
    transactions = transactions.order_by('-created_at')
    
    return render(request, 'main/transactions.html', {
        'transactions': transactions,
        'transaction_type': transaction_type,
        'stats': stats,
        'has_earnings': earnings.exists(),
        'has_spendings': spendings.exists(),
    })

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('home')

@login_required
def find_ride(request):
    """
    Ride search view with filtering capabilities.
    Allows searching by pickup/dropoff locations and sorting options.
    """
    # Initialize form
    form = RideSearchForm()
    rides = Transaction.objects.filter(status='pending')
    
    # Process form data if submitted
    if request.GET:
        form = RideSearchForm(request.GET)
        if form.is_valid():
            pickup = form.cleaned_data.get('pickup')
            dropoff = form.cleaned_data.get('dropoff')
            
            if pickup:
                rides = rides.filter(pickup_location__icontains=pickup)
            if dropoff:
                rides = rides.filter(dropoff_location__icontains=dropoff)
    
    # Handle sorting
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price_low':
        rides = rides.order_by('amount')
    elif sort == 'price_high':
        rides = rides.order_by('-amount')
    else:
        rides = rides.order_by('-created_at')

    return render(request, 'main/find_ride.html', {
        'form': form,
        'rides': rides,
        'current_filters': {
            'pickup': request.GET.get('pickup', ''),
            'dropoff': request.GET.get('dropoff', ''),
            'sort': sort
        }
    })

@login_required
def update_profile(request):
    """Profile update view with form handling"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'main/update_profile.html', {'form': form})

@login_required
def driver_application(request):
    """
    Driver application view.
    Handles driver registration with license upload.
    """
    if request.method == 'POST':
        form = DriverApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.userprofile
            profile.car_model = form.cleaned_data['car_model']
            profile.license_file = form.cleaned_data['license_file']
            profile.driver_status = 'pending'
            profile.is_driver = True  # Set this flag when they apply
            profile.application_date = timezone.now()
            profile.save()
            
            messages.success(request, 'Your driver application has been submitted successfully!')
            return redirect('profile')
    else:
        form = DriverApplicationForm()
    
    return render(request, 'main/driver_application.html', {'form': form})

@login_required
def request_ride(request):
    """Ride request view (placeholder implementation)"""
    if request.method == 'POST':
        # Add your ride request logic here
        return redirect('find_ride')
    return render(request, 'main/find_ride.html')

@login_required
def accept_ride(request, ride_id):
    """
    Ride acceptance view with transaction processing.
    Handles:
    - Ride status update
    - Payment transaction creation
    - Earnings transaction creation
    """
    try:
        # First try to get the ride
        ride = get_object_or_404(Transaction, id=ride_id)
        
        # Check if ride is still pending
        if ride.status != 'pending':
            messages.error(request, 'This ride is no longer available.')
            return redirect('find_ride')
        
        # Don't allow accepting your own ride
        if request.user == ride.user:
            messages.error(request, 'You cannot accept your own ride.')
            return redirect('find_ride')
        
        try:
            with transaction.atomic():  # Atomic transaction
                # Update the ride status
                ride.status = 'accepted'
                ride.driver = request.user
                ride.save()
                
                # Create payment transaction for passenger
                passenger_transaction = Transaction.objects.create(
                    user=ride.user,
                    amount=Decimal(str(-ride.amount)),
                    status='completed',
                    transaction_type='payment',
                    pickup_location=ride.pickup_location,
                    dropoff_location=ride.dropoff_location,
                    description=f'Payment for ride from {ride.pickup_location} to {ride.dropoff_location}'
                )
                
                # Create earning transaction for driver
                driver_transaction = Transaction.objects.create(
                    user=request.user,
                    amount=Decimal(str(ride.amount)),
                    status='completed',
                    transaction_type='earning',
                    pickup_location=ride.pickup_location,
                    dropoff_location=ride.dropoff_location,
                    description=f'Earnings from ride {ride.pickup_location} to {ride.dropoff_location}'
                )
                
                logger.info(f'Ride {ride_id} accepted successfully. Payment: {passenger_transaction.id}, Earning: {driver_transaction.id}')
                messages.success(request, 'Ride accepted successfully!')
                return redirect('transactions')
                
        except Exception as e:
            logger.error(f'Error in transaction processing for ride {ride_id}: {str(e)}')
            messages.error(request, f'Transaction error: {str(e)}')
            return redirect('find_ride')
            
    except Exception as e:
        logger.error(f'Error accepting ride {ride_id}: {str(e)}')
        messages.error(request, f'Error accepting ride: {str(e)}')
        return redirect('find_ride')

@login_required
def complete_ride(request, transaction_id):
    """Ride completion view (placeholder implementation)"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Added ride completion logic here
        messages.success(request, 'Ride completed successfully!')
        return redirect('home')
    except Transaction.DoesNotExist:
        messages.error(request, 'Ride not found.')
        return redirect('home')

@login_required
def cancel_ride(request, transaction_id):
    """Ride cancellation view (placeholder implementation)"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Added ride cancellation logic here
        messages.success(request, 'Ride cancelled successfully!')
        return redirect('home')
    except Transaction.DoesNotExist:
        messages.error(request, 'Ride not found.')
        return redirect('home')

def terms(request):
    """Terms and conditions view"""
    return render(request, 'main/terms.html')

@login_required
def create_ride(request):
    """
    Ride creation view for drivers.
    Validates driver status before allowing ride creation.
    """
    if not request.user.userprofile.is_driver:
        messages.error(request, 'You must be a driver to create rides.')
        return redirect('home')
        
    # Check if driver is pending or rejected
    if request.user.userprofile.driver_status != 'approved':
        messages.warning(request, 'Your driver application is still pending approval. You cannot create rides yet.')
        return redirect('home')

    if request.method == 'POST':
        form = RideCreateForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.user = request.user
            ride.status = 'pending'
            ride.transaction_type = 'ride'
            ride.driver = None
            ride.save()
            messages.success(request, 'Ride posted successfully!')
            return redirect('find_ride')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RideCreateForm()
    
    return render(request, 'main/create_ride.html', {'form': form})

def signup(request):
    """
    User signup view with profile creation.
    Handles both registration and profile setup.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            
            # Create UserProfile with location
            UserProfile.objects.create(
                user=user,
                location=form.cleaned_data.get('location', '')
            )
            
            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
