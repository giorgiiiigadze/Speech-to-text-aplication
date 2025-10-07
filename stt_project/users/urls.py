from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path('api/profile/', UserProfileAPIView.as_view(), name="my_profile"),
    path("api/complete_profile/", CompleteUserProfileAPIView.as_view(), name='complete_profile')
]