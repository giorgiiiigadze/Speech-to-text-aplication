from rest_framework import serializers
from stt.models import AudioFile
from .models import Transcription

class TranscriptionSerializers(serializers.ModelSerializer):
    # show user's uploaded audios as dropdown choices
    audio = serializers.PrimaryKeyRelatedField(
        queryset=AudioFile.objects.all()
    )

    class Meta:
        model = Transcription
        fields = ['id', 'audio', 'user', 'transcribed_text', 'created_at']
        read_only_fields = ['user', 'transcribed_text', 'created_at']
