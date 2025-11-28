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
    waveform_data = models.JSONField(null=True, blank=True)
    transcripted = models.BooleanField(default=False)

    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.file_title
    

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"