from rest_framework import serializers
from .models import *
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import requests

MAILBOXLAYER_API_KEY = "3b5010f6be0ff8429c65ed93d8042e25"

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "username", "email", "first_name", "last_name",
            "password", "confirm_password"
        ]

    def validate_email(self, value):
        validate_email(value)

        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")

        response = requests.get(
            f"http://apilayer.net/api/check?access_key={MAILBOXLAYER_API_KEY}&email={value}"
        ).json()

        if not response.get("format_valid") or not response.get("mx_found"):
            raise serializers.ValidationError("This email address does not exist or domain is invalid.")

        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs


    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Invalid or expired refresh token.'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            self.fail('bad_token')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CompleteUserProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)  
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), 
        source="user", 
        write_only=True
    )

    class Meta:
        model = CompletedUserProfile
        fields = '__all__'
        read_only_fields = ["id", "user", "is_pro"]

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=4000,
        allow_blank=False,
        trim_whitespace=True
    )

    transcription_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    temperature = serializers.FloatField(
        required=False,
        min_value=0.0,
        max_value=1.2
    )

    def validate_transcription_id(self, value):
        if value is None:
            return None
        if not Transcription.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid transcription.")
        return value
