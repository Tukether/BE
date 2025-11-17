from django.contrib import admin
from django.urls import path
from BE.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', health_check, name='root_health_check'),
]