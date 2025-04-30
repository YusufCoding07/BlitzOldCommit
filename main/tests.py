from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile, Transaction

# Create your tests here.

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_profile_creation(self):
        self.assertTrue(hasattr(self.user, 'userprofile'))
        
    def test_profile_update(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('update_profile'), {
            'phone_number': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
