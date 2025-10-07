from django.db import models
from django.conf import settings

class AudioFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='audio/')
    audio_ganre = models.CharField(
        max_length=20,
        choices=[('lesson', 'Lesson'), ('lecture', 'Lecture'), ('podcust', 'Podcust')],
        default='lesson'

    )
    file_title = models.CharField(max_length=50, default='undefined', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('processing', 'Processing'), ('done', 'Done')],
        default='pending'
    )
