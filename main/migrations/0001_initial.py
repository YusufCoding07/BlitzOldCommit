from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('is_driver', models.BooleanField(default=False)),
                ('has_valid_license', models.BooleanField(default=False)),
                ('car_model', models.CharField(blank=True, max_length=100, null=True)),
                ('profile_picture', models.ImageField(blank=True, default='', upload_to='profile_pics/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('driver_status', models.CharField(choices=[('not_applied', 'Not Applied'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='not_applied', max_length=20)),
                ('license_file', models.FileField(blank=True, null=True, upload_to='licenses/')),
                ('application_date', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_location', models.CharField(max_length=200)),
                ('dropoff_location', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ] 