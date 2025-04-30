from django.contrib import admin
from .models import UserProfile, Transaction

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_driver', 'has_valid_license', 'driver_status')
    list_filter = ('is_driver', 'driver_status')
    search_fields = ('user__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'profile_picture')
        }),
        ('Driver Status', {
            'fields': ('is_driver', 'driver_status', 'has_valid_license', 'car_model')
        }),
        ('Application Details', {
            'fields': ('license_file', 'application_date', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['approve_driver', 'reject_driver']

    def approve_driver(self, request, queryset):
        queryset.update(
            is_driver=True,
            driver_status='approved',
            has_valid_license=True
        )
    approve_driver.short_description = "Approve selected driver applications"

    def reject_driver(self, request, queryset):
        queryset.update(
            is_driver=False,
            driver_status='rejected',
            has_valid_license=False
        )
    reject_driver.short_description = "Reject selected driver applications"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pickup_location', 'dropoff_location', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'pickup_location', 'dropoff_location')
    ordering = ('-created_at',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
