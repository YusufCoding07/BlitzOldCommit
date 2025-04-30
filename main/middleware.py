from django.http import HttpResponse
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class DatabaseCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return HttpResponse("Service temporarily unavailable", status=503)
        return self.get_response(request)