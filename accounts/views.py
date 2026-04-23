from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny

from .serializers import LoginSerializer
from .models import User


# 🔷 LOGIN VIEW (PIN AUTH)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # 🔥 ENFORCE PIN CHANGE
            if user.must_change_pin:
                return Response({
                    "message": "PIN change required",
                    "must_change_pin": True,
                    "user_id": user.id
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Login successful",
                "must_change_pin": False,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                }
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔷 CHANGE PIN VIEW
class ChangePinView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        new_pin = request.data.get("new_pin")

        if not user_id or not new_pin:
            return Response({"error": "Missing data"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # 🔥 HASH PIN (VERY IMPORTANT)
        user.pin = make_password(new_pin)
        user.must_change_pin = False
        user.save()

        return Response({"message": "PIN updated successfully"})