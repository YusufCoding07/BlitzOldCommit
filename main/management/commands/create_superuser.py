import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from main.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Superuser already exists.')
            return

        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'

        admin = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Create UserProfile if it doesn't exist
        UserProfile.objects.get_or_create(user=admin)

        self.stdout.write(self.style.SUCCESS('Superuser created successfully'))