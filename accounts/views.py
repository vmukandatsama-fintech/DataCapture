from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.db.models import Q, Sum, Count
from django.db.models.functions import Coalesce
from django.db.models import IntegerField, Value

from .serializers import (
    LoginSerializer, GrowerListSerializer, GrowerDetailSerializer,
    TruckDeliverySerializer, FloorSerializer, RejectionClassificationSerializer,
    RejectedBaleSerializer, ReleaseFromHoldSerializer,
)
from .models import User, Grower, TruckDelivery, Floor, RejectionClassification, RejectedBale, ReleaseFromHold


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


class TruckDeliveryListCreateView(generics.ListCreateAPIView):
    serializer_class = TruckDeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = TruckDelivery.objects.select_related('created_by').all()
        date_from = self.request.query_params.get('date_from', '').strip()
        date_to = self.request.query_params.get('date_to', '').strip()
        area = self.request.query_params.get('area', '').strip()
        if date_from:
            qs = qs.filter(date_expected__gte=date_from)
        if date_to:
            qs = qs.filter(date_expected__lte=date_to)
        if area:
            qs = qs.filter(area__iexact=area)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)

        # Interim totals for the current filter
        interim = qs.aggregate(
            interim_booked=Coalesce(Sum('qty_booked'), Value(0), output_field=IntegerField()),
            interim_offloaded=Coalesce(Sum('qty_offloaded'), Value(0), output_field=IntegerField()),
        )

        # Overall totals (all records, all dates)
        overall = TruckDelivery.objects.aggregate(
            total_booked=Coalesce(Sum('qty_booked'), Value(0), output_field=IntegerField()),
            total_offloaded=Coalesce(Sum('qty_offloaded'), Value(0), output_field=IntegerField()),
        )
        balance_outstanding = overall['total_booked'] - overall['total_offloaded']

        return Response({
            'results': serializer.data,
            'summary': {
                'interim_booked': interim['interim_booked'],
                'interim_offloaded': interim['interim_offloaded'],
                'interim_difference': interim['interim_booked'] - interim['interim_offloaded'],
                'total_expected': overall['total_booked'],
                'balance_outstanding': balance_outstanding,
            }
        })

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TruckDeliveryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TruckDeliverySerializer
    permission_classes = [IsAuthenticated]
    queryset = TruckDelivery.objects.select_related('created_by').all()


class TruckAreaListView(APIView):
    """Returns distinct areas from Grower table for autocomplete."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        areas = list(
            Grower.objects.values_list('area', flat=True).distinct().order_by('area')
        )
        return Response(areas)


class FloorListView(generics.ListAPIView):
    serializer_class = FloorSerializer
    permission_classes = [IsAuthenticated]
    queryset = Floor.objects.all()


class RejectionClassificationListView(generics.ListAPIView):
    serializer_class = RejectionClassificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = RejectionClassification.objects.all()


class RejectedBaleListCreateView(generics.ListCreateAPIView):
    serializer_class = RejectedBaleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RejectedBale.objects.select_related(
            'floor', 'classification', 'created_by'
        ).all()
        date_from = self.request.query_params.get('date_from', '').strip()
        date_to = self.request.query_params.get('date_to', '').strip()
        floor_id = self.request.query_params.get('floor', '').strip()
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if floor_id:
            qs = qs.filter(floor_id=floor_id)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        total = qs.count()
        return Response({'results': serializer.data, 'total': total})

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class RejectedBaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RejectedBaleSerializer
    permission_classes = [IsAuthenticated]
    queryset = RejectedBale.objects.select_related('floor', 'classification', 'created_by').all()


class ReleaseFromHoldListCreateView(generics.ListCreateAPIView):
    serializer_class = ReleaseFromHoldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ReleaseFromHold.objects.select_related(
            'floor', 'rejected_bale__classification', 'created_by'
        ).all()
        date_from = self.request.query_params.get('date_from', '').strip()
        date_to = self.request.query_params.get('date_to', '').strip()
        floor_id = self.request.query_params.get('floor', '').strip()
        resolution = self.request.query_params.get('resolution', '').strip()
        if date_from:
            qs = qs.filter(resolution_date__gte=date_from)
        if date_to:
            qs = qs.filter(resolution_date__lte=date_to)
        if floor_id:
            qs = qs.filter(floor_id=floor_id)
        if resolution:
            qs = qs.filter(resolution=resolution)
        return qs

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response({'results': serializer.data, 'total': qs.count()})

    def perform_create(self, serializer):
        ticket = serializer.validated_data.get('ticket_number', '')
        bale = RejectedBale.objects.filter(ticket_number=ticket).first()
        serializer.save(created_by=self.request.user, rejected_bale=bale)


class ReleaseFromHoldDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReleaseFromHoldSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReleaseFromHold.objects.select_related('floor', 'rejected_bale', 'created_by').all()


class TicketLookupView(APIView):
    """Search rejected bales by ticket number for the release form."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response([])
        qs = RejectedBale.objects.filter(ticket_number__icontains=q).select_related('floor', 'classification')[:10]
        return Response([{
            'id': b.id,
            'ticket_number': b.ticket_number,
            'date': str(b.date),
            'floor_id': b.floor_id,
            'floor_name': b.floor.name,
            'grower_number': b.grower_number,
            'grower_name': b.grower_name,
            'classification_code': b.classification.code,
            'lot_number': b.lot_number,
        } for b in qs])


class GrowerLookupView(APIView):
    """Quick grower lookup by grower_id or name fragment for autocomplete."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response([])
        qs = Grower.objects.filter(
            Q(grower_id__icontains=q) | Q(grower_name__icontains=q)
        )[:15]
        return Response([
            {
                'grower_id': g.grower_id,
                'grower_name': g.grower_name,
                'group_code': g.group_code,
                'group_name': g.group_name,
            }
            for g in qs
        ])
