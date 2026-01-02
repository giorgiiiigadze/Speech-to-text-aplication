from django.db import models
from django.conf import settings
from stt.models import AudioFile


class Transcription(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transcriptions",
    )
    audio = models.OneToOneField(
        AudioFile,
        on_delete=models.CASCADE,
        related_name="transcription",
    )

    transcribed_text = models.TextField(blank=True)
    transcription_tag = models.CharField(max_length=100, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription #{self.id} ({self.status})"
