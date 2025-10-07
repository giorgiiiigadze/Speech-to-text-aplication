from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
import whisper
import os

from stt.models import AudioFile
from .models import Transcription
from .serializers import TranscriptionSerializers

class AudioTranscribeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get_serializer_class(self):
        # You can customize this later if needed for GET vs POST
        return self.serializer_class

    def post(self, request, pk):
        # Get the user's uploaded audio file by ID
        audio_instance = get_object_or_404(AudioFile, pk=pk, user=request.user)

        # Ensure ffmpeg is on PATH (for Windows)
        os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

        try:
            # Load Whisper model
            model = whisper.load_model("base")

            # Transcribe the file
            result = model.transcribe(audio_instance.file.path)
            transcribed_text = result["text"]

            # Save transcription record
            transcription = Transcription.objects.create(
                audio=audio_instance,
                user=request.user,
                transcribed_text=transcribed_text
            )


            return Response({
                "message": "Transcription completed successfully.",
                "audio_id": audio_instance.id,
                "transcription_id": transcription.id,
                "transcribed_text": transcribed_text
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"Error during transcription: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
