from celery import shared_task
from .models import Transcription
from .transcription_service import transcribe_audio

@shared_task
def transcribe_audio_task(transcription_id):
    transcription = Transcription.objects.get(id=transcription_id)

    transcription.status = "PROCESSING"
    transcription.save(update_fields=["status"])

    try:
        text, tag = transcribe_audio(transcription.audio.file.path)

        transcription.transcribed_text = text
        transcription.transcription_tag = tag
        transcription.status = "DONE"
        transcription.save()

    except Exception:
        transcription.status = "FAILED"
        transcription.save()
        raise
