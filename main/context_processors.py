from django.core.cache import cache
from .models import UserProfile

def user_profile(request):
    if request.user.is_authenticated:
        cache_key = f'user_profile_{request.user.id}'
        profile = cache.get(cache_key)
        
        if profile is None:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            cache.set(cache_key, profile, 300)  # Cache for 5 minutes
            
        return {'user_profile': profile}
    return {'user_profile': None}