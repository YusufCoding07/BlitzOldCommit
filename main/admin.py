# Import Django admin module
from django.contrib import admin
# Import models from current application
from .models import UserProfile, Transaction

# Admin configuration for UserProfile model
class UserProfileAdmin(admin.ModelAdmin):
    """
    Custom admin interface for UserProfile model with:
    - List display configuration
    - Filtering options
    - Search functionality
    - Fieldset organization
    - Custom admin actions
    """
    
    # Fields to display in list view
    list_display = ('user', 'phone_number', 'is_driver', 'has_valid_license', 'driver_status')
    
    # Filters for the right sidebar
    list_filter = ('is_driver', 'driver_status')
    
    # Searchable fields
    search_fields = ('user__username', 'phone_number')
    
    # Fields that should be read-only
    readonly_fields = ('created_at', 'updated_at')
    
    # Organized field groupings for detail view
    fieldsets = (
        # User Information section
        ('User Information', {
            'fields': ('user', 'phone_number', 'profile_picture')
        }),
        
        # Driver Status section
        ('Driver Status', {
            'fields': ('is_driver', 'driver_status', 'has_valid_license', 'car_model')
        }),
        
        # Application Details section
        ('Application Details', {
            'fields': ('license_file', 'application_date', 'admin_notes')
        }),
        
        # Timestamps section (collapsible)
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Makes this section collapsible
        })
    )

    # Custom admin actions
    actions = ['approve_driver', 'reject_driver']

    def approve_driver(self, request, queryset):
        """
        Bulk approve driver applications
        Sets:
        - is_driver = True
        - driver_status = 'approved'
        - has_valid_license = True
        """
        queryset.update(
            is_driver=True,
            driver_status='approved',
            has_valid_license=True
        )
    approve_driver.short_description = "Approve selected driver applications"

    def reject_driver(self, request, queryset):
        """
        Bulk reject driver applications
        Sets:
        - is_driver = False
        - driver_status = 'rejected'
        - has_valid_license = False
        """
        queryset.update(
            is_driver=False,
            driver_status='rejected',
            has_valid_license=False
        )
    reject_driver.short_description = "Reject selected driver applications"

# Admin configuration for Transaction model
class TransactionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Transaction model with:
    - List display configuration
    - Filtering options
    - Search functionality
    - Default ordering
    """
    
    # Fields to display in list view
    list_display = ('id', 'user', 'pickup_location', 'dropoff_location', 'amount', 'status', 'created_at')
    
    # Filters for the right sidebar
    list_filter = ('status', 'created_at')
    
    # Searchable fields
    search_fields = ('user__username', 'pickup_location', 'dropoff_location')
    
    # Default sorting (newest first)
    ordering = ('-created_at',)

# Register models with their custom admin classes
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Transaction, TransactionAdmin)
