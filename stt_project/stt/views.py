import json
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from transcriptions.models import *
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .throttles import *

# Caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from transcriptions.serializers import *
import os

class MyUploadedAudio(generics.ListAPIView):
    throttle_scope = 'my_audios'
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['file_title', 'status', 'transcripted', 'favorite']

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)

class AudioDetailGenericView(generics.RetrieveDestroyAPIView):
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.file and os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
        instance.delete()

class AudioUploadView(generics.CreateAPIView):
    throttle_scope = 'audio_upload'

    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')
            
class AudioDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        audio = get_object_or_404(AudioFile, pk=pk, user=request.user)
        
        if audio.file and os.path.isfile(audio.file.path):
            os.remove(audio.file.path)

        if audio.waveform_file and os.path.isfile(audio.waveform_file.path):
            os.remove(audio.waveform_file.path)

        audio.delete()

        return Response({"message": "Audio deleted successfully."}, status=status.HTTP_200_OK)

class AudioEditTitleView(generics.UpdateAPIView):
    throttle_scope = 'edit_audios_title'
    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        audio = self.get_object()

        new_title = request.data.get("file_title")
        if not new_title:
            return Response(
                {"error": "file_title is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        audio.file_title = new_title
        audio.save()

        return Response({
            "id": audio.id,
            "file_title": audio.file_title,
            "message": "Audio title updated successfully."
        })
    
class AudioFavoriteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        audio = get_object_or_404(AudioFile, pk=pk, user=request.user)
        
        if "favorite" in request.data:
            audio.favorite = bool(request.data["favorite"])
        else:
            audio.favorite = not audio.favorite
        
        audio.save()

        return Response({
            "id": audio.id,
            "file_title": audio.file_title,
            "favorite": audio.favorite,
            "message": f"Audio {'added to' if audio.favorite else 'removed from'} favorites."
        }, status=status.HTTP_200_OK)

class AudioCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = AudioCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == "POST":
            return [AudioCommentThrottle()]
        return []

    def get_queryset(self):
        audio_id = self.kwargs["audio_id"]
        get_object_or_404(AudioFile, id=audio_id, user=self.request.user)
        return Comment.objects.filter(audio_id=audio_id)

    def perform_create(self, serializer):
        audio_id = self.kwargs["audio_id"]
        audio = get_object_or_404(AudioFile, id=audio_id)
        serializer.save(user=self.request.user, audio=audio)
        
class AudioCommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AudioCommentDeleteThrottle]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)
    
class AudioCommentTypeUpdateView(generics.UpdateAPIView):
    serializer_class = CommentTypeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

from stt.tasks import generate_waveform_task

class AudioWaveformView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        audio = get_object_or_404(AudioFile, pk=pk, user=request.user)

        if audio.waveform_file and audio.status == "done":
            with open(audio.waveform_file.path) as f:
                waveform = json.load(f)

            return Response({
                "status": "done",
                "waveform": waveform
            }, status=200)

        if audio.status != "processing":
            audio.status = "processing"
            audio.save(update_fields=["status"])

        generate_waveform_task.delay(audio.id)

        return Response({
            "status": "processing",
            "message": "Waveform generation running"
        }, status=202)
