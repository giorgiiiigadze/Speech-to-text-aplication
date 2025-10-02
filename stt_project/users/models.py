from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class CompletedUserProfile(models.Model):
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
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
