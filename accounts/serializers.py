from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from .utils import verify_pin

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    pin = serializers.CharField()

    def validate(self, data):
        username = data.get("username")
        pin = data.get("pin")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        if not verify_pin(pin, user.pin):
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data