from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.conf import settings
from transcriptions.models import *

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class CompletedUserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    profile_status = models.CharField(
        max_length=20,
        choices=[('active', 'Active'), ('away', 'Away'), ('offline', 'Offline')],
        default='lesson'
    )

    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_pro = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class ChatMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    transcripted_audio = models.ForeignKey(
        Transcription,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f"Message from {self.user.username} at {self.timestamp}"