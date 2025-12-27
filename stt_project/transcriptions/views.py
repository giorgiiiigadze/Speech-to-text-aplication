from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from stt.models import AudioFile
from .models import Transcription
from .serializers import TranscriptionSerializers

import whisper
import os

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def generate_tag(text: str) -> str:
    examples = """
        Input: Helloo kids, today we are learning about biology
        Output: Biology class

        Input: The capital city of America is Washington D.C
        Output: Geography class

        Input: We will solve equations involving quadratic functions
        Output: Math class

        Input: Shakespeare wrote many famous plays
        Output: Literature class
    """

    prompt = PromptTemplate(
        input_variables=["sentence"],
        template=(
            "Generate a short 2–3 word title describing the following text.\n\n"
            f"{examples}\n"
            "Input: {sentence}\n"
            "Output:"
        ),
    )

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0,
    )

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"sentence": text})
    return result.strip()

class AudioTranscribeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get(self, request, pk):
        transcription = Transcription.objects.filter(
            audio__id=pk, user=request.user
        ).first()

        if not transcription:
            return Response(
                {"error": "No transcription found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "audio_id": transcription.audio.id,
                "transcription_id": transcription.id,
                "transcribed_text": transcription.transcribed_text,
                "transcription_tag": transcription.transcription_tag,
                "transcripted": transcription.transcripted,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        audio_instance = get_object_or_404(
            AudioFile, pk=pk, user=request.user
        )

        os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

        transcription = Transcription.objects.filter(
            audio=audio_instance, user=request.user
        ).first()

        if transcription and transcription.transcripted:
            return Response(
                {"message": "This audio has already been transcribed."},
                status=status.HTTP_200_OK,
            )

        try:
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_instance.file.path, fp16=False)

            transcribed_text = result["text"].strip()
            transcription_tag = generate_tag(transcribed_text)

            if transcription:
                transcription.transcribed_text = transcribed_text
                transcription.transcription_tag = transcription_tag
                transcription.transcripted = True
                transcription.save()
            else:
                transcription = Transcription.objects.create(
                    audio=audio_instance,
                    user=request.user,
                    transcribed_text=transcribed_text,
                    transcription_tag=transcription_tag,
                    transcripted=True,
                )

            return Response(
                {
                    "message": "Transcription completed successfully.",
                    "audio_id": audio_instance.id,
                    "transcription_id": transcription.id,
                    "transcribed_text": transcribed_text,
                    "transcription_tag": transcription_tag,
                    "transcripted": transcription.transcripted,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Error during transcription: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def patch(self, request, pk):
        transcription = get_object_or_404(
            Transcription, audio__id=pk, user=request.user
        )

        serializer = self.get_serializer(
            transcription, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Transcription updated successfully.",
                    "audio_id": transcription.audio.id,
                    "transcription_id": transcription.id,
                    "transcribed_text": transcription.transcribed_text,
                    "transcription_tag": transcription.transcription_tag,
                    "transcripted": transcription.transcripted,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class MyTranscriptedAudio(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptionSerializers

    def get(self, request):
        transcriptions = Transcription.objects.filter(
            user=request.user, transcripted=True
        )

        if not transcriptions.exists():
            return Response(
                {"message": "No transcribed audios found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(transcriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
