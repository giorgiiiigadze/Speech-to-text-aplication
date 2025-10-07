from django.db import models
from django.conf import settings
from stt.models import AudioFile

class Transcription(models.Model):
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name="transcription")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    transcribed_text = models.TextField(blank=True)
