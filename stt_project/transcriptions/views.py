from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from stt.models import AudioFile
from .models import Transcription
from .serializers import TranscriptionSerializers
from .tasks import transcribe_audio_task


class AudioTranscribeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get_audio(self, pk, user):
        return get_object_or_404(AudioFile, pk=pk, user=user)

    def get(self, request, pk):
        transcription = get_object_or_404(
            Transcription,
            audio__id=pk,
            user=request.user
        )
        serializer = self.get_serializer(transcription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        audio = self.get_audio(pk, request.user)

        with transaction.atomic():
            transcription, created = Transcription.objects.get_or_create(
                audio=audio,
                user=request.user,
                defaults={"status": "PENDING"},
            )

            # ✅ Already finished → no celery
            if transcription.status == "DONE":
                serializer = self.get_serializer(transcription)
                return Response(
                    {
                        "detail": "This audio has already been transcribed.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            # 🚫 Prevent duplicate tasks
            if transcription.status == "PROCESSING":
                serializer = self.get_serializer(transcription)
                return Response(
                    serializer.data,
                    status=status.HTTP_202_ACCEPTED,
                )

            # ✅ Mark PROCESSING BEFORE celery
            transcription.status = "PROCESSING"
            transcription.save(update_fields=["status"])

            # ✅ Run celery ONLY after DB commit
            transaction.on_commit(
                lambda: transcribe_audio_task.delay(transcription.id)
            )

        serializer = self.get_serializer(transcription)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def patch(self, request, pk):
        transcription = get_object_or_404(
            Transcription,
            audio__id=pk,
            user=request.user
        )

        serializer = self.get_serializer(
            transcription,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MyTranscriptedAudio(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get_queryset(self):
        return Transcription.objects.filter(user=self.request.user)


class TranscriptionStatusView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get_object(self):
        return get_object_or_404(
            Transcription,
            audio__id=self.kwargs["pk"],
            user=self.request.user
        )
