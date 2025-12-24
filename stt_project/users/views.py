from django.shortcuts import render
from django.conf import settings
from .serializers import *
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def llm_function():
    llm = ChatOpenAI(openai_api_key=api_key, temperature=0)
    return llm

def prompt_function():
    prompt = PromptTemplate(
        input_variables=["user_input"],
        template=(
            "You are Voicify's helpful assistant.\n"
            "You help users understand website features and answer questions about speech-to-text technology.\n"
            "Respond clearly and concisely to the user's message below:\n\n"
            "User: {user_input}\nAI:"
        ),
    )
    return prompt

llm = llm_function()
prompt = prompt_function()
parser = StrOutputParser()

llm_chain = RunnableSequence(prompt | llm | parser)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    def get(self, request):
        return Response({"message": "Send a POST request to register a user."})
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Use POST to logout. Send your refresh token in the body."})

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user

class CompleteUserProfileAPIView(generics.ListCreateAPIView):
    queryset = CompletedUserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteUserProfileSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        profiles = CompletedUserProfile.objects.filter(user=user)
        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatbotAPIView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.validated_data["message"]
        transcription_obj = serializer.validated_data.get("transcripted_audio", None)
        ai_input = f"User instruction: {user_message}"
        if transcription_obj:
            ai_input += (
                f"\n\nTranscribed Audio Content:\n{transcription_obj.transcribed_text}\n"
                "Modify or analyze this text as requested by the user. "
                "If there is no text, return a message saying there is no text."
            )
        try:
            ai_reply = llm_chain.invoke({"user_input": ai_input})
            return Response({"ai_result": ai_reply}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
