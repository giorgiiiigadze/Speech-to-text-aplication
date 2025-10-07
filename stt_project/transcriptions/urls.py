from django.urls import path
from .views import *

urlpatterns = [
    path('audio/<int:pk>/', AudioTranscribeView.as_view(), name='audio-transcribe'),
]