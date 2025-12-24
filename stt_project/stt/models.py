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
    waveform_file = models.FileField(upload_to='waveforms/', null=True, blank=True)
    transcripted = models.BooleanField(default=False)

    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.file_title

class Comment(models.Model):
    COMMENT_TYPES = [
        ("idea", "Idea"),
        ("issue", "Issue"),
        ("edit", "Edit"),
        ("note", "Note"),
        ("task", "Task"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    audio = models.ForeignKey(
        "AudioFile",
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )

    content = models.TextField()

    comment_status = models.CharField(
        max_length=20,
        choices=[('Not started', 'not started'), ('In progress', 'in progress'), ('Done', 'done')],
        default='Not started'
    )
    
    comment_type = models.CharField(
        max_length=20,
        choices=COMMENT_TYPES,
        default="idea",
    )

    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"