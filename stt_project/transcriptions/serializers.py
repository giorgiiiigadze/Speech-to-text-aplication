from rest_framework import serializers
from stt.models import AudioFile
from .models import Transcription

class TranscriptionSerializers(serializers.ModelSerializer):
    audio = serializers.PrimaryKeyRelatedField(
        queryset=AudioFile.objects.all()
    )

    class Meta:
        model = Transcription
        fields = '__all__'
        read_only_fields = ['audio', 'user', 'created_at', 'transcripted', 'transcription_tag', 'transcribed_text']
