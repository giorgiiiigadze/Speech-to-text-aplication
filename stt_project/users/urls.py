from django.contrib import admin
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/profile/', UserProfileAPIView.as_view(), name="my_profile"),
    path("api/completed_profile/", CompleteUserProfileAPIView.as_view(), name='completed_profile'),
    path("api/chat_bot/", ChatbotAPIView.as_view(), name='chat_bot')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)