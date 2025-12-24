from django.contrib import admin
from .models import AudioFile, Comment

@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    # search_fields = ('user__username', 'transcription_text')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class AudioCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'audio', 'content', 'created_at')