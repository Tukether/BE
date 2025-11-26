# TukCommunityBE/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # accounts 앱의 URL들을 /api/accounts/ 밑으로 연결
    path('api/accounts/', include('sources.accounts.urls')), 
]