# Import Django test modules and required components
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, Transaction

class UserProfileTests(TestCase):
    """
    Test suite for UserProfile model and related functionality.
    Includes tests for profile creation and updates.
    """
    
    def setUp(self):
        """
        Set up test environment before each test method runs.
        Creates:
        - A test client for simulating HTTP requests
        - A test user for authentication
        """
        self.client = Client()  # Django test client
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_profile_creation(self):
        """
        Test that a UserProfile is automatically created
        when a new User is created (via signal).
        Verifies:
        - The user has a userprofile attribute
        """
        self.assertTrue(hasattr(self.user, 'userprofile'),
            "UserProfile should be automatically created for new users"
        
    def test_profile_update(self):
        """
        Test profile updating through the update_profile view.
        Verifies:
        - Successful login
        - Profile update returns redirect status (302)
        """
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Simulate profile update POST request
        response = self.client.post(reverse('update_profile'), {
            'phone_number': '1234567890'  # Test update data
        })
        
        # Verify the response is a redirect (typically to profile page)
        self.assertEqual(response.status_code, 302,
            "Profile update should redirect after successful submission")

# Additional test classes can be added here following the same pattern:
# class TransactionTests(TestCase):
#     def setUp(self):
#         # Setup for transaction tests
#     
#     def test_transaction_creation(self):
#         # Test transaction creation
#
#     def test_transaction_status_update(self):
#         # Test transaction status changes
