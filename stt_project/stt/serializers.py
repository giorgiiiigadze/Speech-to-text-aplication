from rest_framework import serializers
from .models import *
from pydub import AudioSegment

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status', 'created_at']

    # We will change this part over the time
    def validate_file(self, value):
            # Declaring valid file types
            valid_extensions = ['.mp3', '.wav', '.ogg', '.m4a']
            # Checking our files type
            ext = value.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise serializers.ValidationError("Unsupported file type. Allowed: mp3, wav, ogg, m4a.")

            # The max size of the file is 10MB
            max_size = 10 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("File too large. Maximum size is 10MB.")

            try:
                audio = AudioSegment.from_file(value)
                duration_seconds = len(audio) / 1000
                # Checking if the audio is longer than 5 minutes
                if duration_seconds > 5 * 60:
                    raise serializers.ValidationError("Audio too long. Maximum duration is 5 minutes.")
            except Exception:
                raise serializers.ValidationError("Could not read audio file.")

            return value

class AudioCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = '__all__'