from rest_framework import serializers
from .models import AudioFile

class TranscriptionSerializers(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
