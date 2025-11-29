from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, LogoutView

urlpatterns = [
    # 회원가입
    path('signup/', RegisterView.as_view(), name='signup'),

    # 로그인 (토큰 발급)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # 토큰 재발급
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 로그아웃
    path('logout/', LogoutView.as_view(), name='logout'),
]