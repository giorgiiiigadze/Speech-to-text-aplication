from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', UserProfileAPIView.as_view(), name="my_profile"),
    path("complete_profile/", CompleteUserProfileAPIView.as_view(), name='complete_profile')
]