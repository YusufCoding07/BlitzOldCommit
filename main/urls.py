# main/urls.py
from django.urls import path
from . import views

# Define URL patterns for the application
urlpatterns = [
    # Home page URL
    path('', views.home, name='home'),
    
    # User authentication URLs
    path('register/', views.register, name='register'),  # User registration
    path('login/', views.login_view, name='login'),      # User login
    path('logout/', views.logout_view, name='logout'),   # User logout
    path('signup/', views.register, name='signup'),      # Alias for registration
    
    # User profile URLs
    path('profile/', views.profile, name='profile'),               # Profile view
    path('profile/update/', views.update_profile, name='update_profile'),  # Profile update
    
    # Ride-related URLs
    path('find-ride/', views.find_ride, name='find_ride'),         # Find available rides
    path('request-ride/', views.request_ride, name='request_ride'),  # Request a new ride
    path('rides/create/', views.create_ride, name='create_ride'),   # Create a new ride offer
    
    # Ride action URLs (with ride/transaction IDs)
    path('accept-ride/<int:ride_id>/', views.accept_ride, name='accept_ride'),       # Accept a ride
    path('complete-ride/<int:transaction_id>/', views.complete_ride, name='complete_ride'),  # Complete ride
    path('cancel-ride/<int:transaction_id>/', views.cancel_ride, name='cancel_ride'),  # Cancel ride
    
    # Transaction history URL
    path('transactions/', views.transactions, name='transactions'),  # Transaction history view
    
    # Driver application URL
    path('driver-application/', views.driver_application, name='driver_application'),  # Driver signup
    
    # Miscellaneous URLs
    path('map/', views.map_view, name='map'),      # Map view
    path('terms/', views.terms, name='terms'),     # Terms and conditions
    
    # Additional URLs can be added here following the same pattern:
    # path('new-path/', views.view_function, name='url_name'),
]
