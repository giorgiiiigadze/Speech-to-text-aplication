from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from transcriptions.models import *
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from transcriptions.serializers import *
import os

# Audio waveform generation part
from pydub import AudioSegment
import numpy as np

def generate_waveform_data(audio_path, points=120):
    try:
        sound = AudioSegment.from_file(audio_path)
        samples = np.array(sound.get_array_of_samples())

        if sound.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)

        samples = np.abs(samples)
        max_val = np.max(samples)
        if max_val == 0:
            return [0] * points

        samples = samples / max_val

        chunk_size = len(samples) // points
        waveform = [
            float(np.max(samples[i:i + chunk_size]))
            for i in range(0, len(samples), chunk_size)
        ]

        return waveform[:points]
    except Exception as e:
        print("Waveform generation error:", e)
        return [0] * points



class AudioUploadView(generics.CreateAPIView):
    throttle_scope = 'audio_upload'

    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')
            
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

class MyUploadedAudio(generics.ListAPIView):
    throttle_scope = 'my_audios'

    serializer_class = AudioFileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['file_title', 'status', 'transcripted', 'favorite']

    def patch(self, request, pk=None):
        audio_id = pk or request.data.get("id") or request.query_params.get("id")
        if not audio_id:
            return Response({"error": "Audio ID (id) is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        audio = get_object_or_404(AudioFile, id=audio_id, user=request.user)

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
    
    def get_queryset(self):
        return AudioFile.objects.filter(user=self.request.user)
    
class AudioCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = AudioCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        audio_id = self.kwargs['audio_id']
        get_object_or_404(AudioFile, id=audio_id, user=self.request.user)
        return Comment.objects.filter(audio_id=audio_id)
    
    def perform_create(self, serializer):
        audio_id = self.kwargs['audio_id']
        audio = get_object_or_404(AudioFile, id=audio_id)
        serializer.save(user=self.request.user, audio=audio)

class AudioWaveformView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        audio = get_object_or_404(AudioFile, pk=pk, user=request.user)

        if not audio.file or not os.path.isfile(audio.file.path):
            return Response({"error": "Audio file not found."}, status=404)

        if audio.status == 'done' and audio.waveform_data:
            return Response({
                "status": "done",
                "waveform": audio.waveform_data
            }, status=200)

        elif audio.status in ['pending', 'processing']:
            if audio.status == 'pending':
                audio.status = 'processing'
                audio.save()

            return Response({
                "status": audio.status,
                "message": "Audio is being processed. Please check back later."
            }, status=202)
        
        else:
            from .views import generate_waveform_data
            waveform = generate_waveform_data(audio.file.path)
            audio.waveform_data = waveform
            audio.status = 'done'
            audio.save()
            return Response({
                "status": "done",
                "waveform": waveform
            }, status=200)