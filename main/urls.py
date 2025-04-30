# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('transactions/', views.transactions, name='transactions'),  # Add this line
    path('map/', views.map_view, name='map'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('find-ride/', views.find_ride, name='find_ride'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('driver-application/', views.driver_application, name='driver_application'),
    path('request-ride/', views.request_ride, name='request_ride'),
    path('accept-ride/<int:ride_id>/', views.accept_ride, name='accept_ride'),
    path('complete-ride/<int:transaction_id>/', views.complete_ride, name='complete_ride'),
    path('cancel-ride/<int:transaction_id>/', views.cancel_ride, name='cancel_ride'),
    path('signup/', views.register, name='signup'),
    path('terms/', views.terms, name='terms'),
    path('rides/create/', views.create_ride, name='create_ride'),
]