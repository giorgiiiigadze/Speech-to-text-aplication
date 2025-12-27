import logging

from django.core.cache import cache
from django.conf import settings

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import get_authorization_header

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    RegisterSerializer,
    LogoutSerializer,
    UserProfileSerializer,
    CompleteUserProfileSerializer,
    ChatRequestSerializer,
)
from .models import *
from .services import ChatService
from .throttles import ChatThrottle
from .utils import sanitize_text

from transcriptions.models import Transcription

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "User registered successfully."},
            status=status.HTTP_201_CREATED,
        )

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )

        except TokenError as e:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserProfileAPIView(generics.RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class CompleteUserProfileAPIView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteUserProfileSerializer

    def get_queryset(self):
        return CompletedUserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatThrottle]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_service = ChatService()

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        message = sanitize_text(serializer.validated_data["message"])
        temperature = serializer.validated_data.get("temperature")
        transcription_id = serializer.validated_data.get("transcription_id")

        transcription = None
        if transcription_id:
            try:
                transcription = Transcription.objects.get(
                    id=transcription_id,
                    user=user,
                )
            except Transcription.DoesNotExist:
                return Response(
                    {"detail": "Invalid transcription reference."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        token = get_authorization_header(request).decode("utf-8")
        cache_key = f"chat:{user.id}:{hash(message)}:{hash(token)}"

        cached = cache.get(cache_key)
        if cached:
            return Response(cached, status=status.HTTP_200_OK)

        ChatMessage.objects.create(
            user=user,
            message=message,
            transcripted_audio=transcription,
        )

        try:
            ai_reply = self.chat_service.generate_reply(
                user=user,
                user_message=message,
                temperature=temperature,
            )
        except Exception:
            logger.exception("AI generation failed")
            return Response(
                {"detail": "AI service unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        ChatMessage.objects.create(
            user=user,
            message=ai_reply,
            transcripted_audio=transcription,
        )

        response = {"assistant": ai_reply}

        cache.set(cache_key, response, timeout=30)

        return Response(response, status=status.HTTP_200_OK)
