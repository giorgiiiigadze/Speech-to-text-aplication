from rest_framework import serializers
from .models import AudioFile, Comment
from pydub import AudioSegment


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "status",
            "created_at",
            "waveform_file",
            "transcripted",
        ]

    def validate(self, attrs):
        file = attrs.get("file")

        if not file:
            return attrs

        valid_extensions = [".mp3", ".wav", ".ogg", ".m4a"]
        ext = f".{file.name.lower().split('.')[-1]}"
        if ext not in valid_extensions:
            raise serializers.ValidationError({
                "file": "Unsupported file type. Allowed: mp3, wav, ogg, m4a."
            })

        max_size = 50 * 1024 * 1024
        if file.size > max_size:
            raise serializers.ValidationError({
                "file": "File too large. Maximum size is 50MB."
            })

        try:
            audio = AudioSegment.from_file(file)
            duration_seconds = len(audio) / 1000

            if duration_seconds > 5 * 60:
                raise serializers.ValidationError({
                    "file": "Audio too long. Maximum duration is 5 minutes."
                })

        except Exception:
            raise serializers.ValidationError({
                "file": "Could not read audio file."
            })

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("file", None)
        return super().update(instance, validated_data)


class AudioCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "audio",
            "created_at",
            "comment_status",
            "expires_at",
        ]

class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]

class CommentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["status"]

class CommentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["comment_type"]
