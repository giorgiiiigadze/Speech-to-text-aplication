from django.db import models
from django.conf import settings
from stt.models import AudioFile

class Transcription(models.Model):
    audio = models.OneToOneField(AudioFile, on_delete=models.CASCADE, related_name="transcription")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
