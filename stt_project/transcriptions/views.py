from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from stt.models import AudioFile
from .serializers import TranscriptionSerializers
import whisper
import os
