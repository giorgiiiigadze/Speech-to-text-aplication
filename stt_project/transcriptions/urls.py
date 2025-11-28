from django.urls import path
from .views import *

urlpatterns = [
    path('api/transcripted_audios/', MyTranscriptedAudio.as_view(), name='my-transcripted-audio'),
    path('api/audio/<int:pk>/', AudioTranscribeView.as_view(), name='audio-transcribe'),
]