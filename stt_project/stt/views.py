from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AudioFile
from .serializers import AudioFileSerializer
from django.shortcuts import get_object_or_404
from transcriptions.models import *
from rest_framework.permissions import IsAuthenticated
import whisper
import os

class AudioUploadView(generics.CreateAPIView):
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        audio_instance = serializer.save(user=self.request.user, status='processing')

        os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

        try:
            model = whisper.load_model("base")

            result = model.transcribe(audio_instance.file.path)

            audio_instance.transcribed_text = result["text"]
            audio_instance.status = 'done'
            audio_instance.save()

        except Exception as e:
            audio_instance.status = 'pending'
            audio_instance.save()
            print("Error transcribing audio:", e)
            
class AudioDetailGenericView(generics.RetrieveAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)

class MyUploadedAudio(generics.ListAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user = self.request.user)


class AudioStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        audio = get_object_or_404(AudioFile, pk=pk, user=request.user)
        serializer = AudioFileSerializer(audio)
        return Response(serializer.data)
    