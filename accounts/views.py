from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db.models import Q

from .serializers import LoginSerializer, GrowerListSerializer, GrowerDetailSerializer
from .models import User, Grower


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

            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "must_change_pin": False,
                "access_token": str(refresh.access_token),
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

        # Update PIN
        user.pin = make_password(new_pin)
        user.must_change_pin = False
        user.save()

        # 🔥 ISSUE TOKEN IMMEDIATELY
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "PIN updated successfully",
            "access_token": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            }
        })


class GrowerListView(generics.ListAPIView):
    serializer_class = GrowerListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Grower.objects.all()
        search = self.request.query_params.get('search', '').strip()
        scheme = self.request.query_params.get('scheme', '').strip()
        area_code = self.request.query_params.get('area_code', '').strip()
        group_code = self.request.query_params.get('group_code', '').strip()

        if search:
            qs = qs.filter(
                Q(grower_id__icontains=search) | Q(grower_name__icontains=search)
            )
        if scheme:
            qs = qs.filter(scheme=scheme)
        if area_code:
            qs = qs.filter(area_code=area_code)
        if group_code:
            qs = qs.filter(group_code=group_code)

        return qs


class GrowerDetailView(generics.RetrieveAPIView):
    serializer_class = GrowerDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Grower.objects.all()
    lookup_field = 'grower_id'