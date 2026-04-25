from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Grower, TruckDelivery, Floor, RejectionClassification, RejectedBale, ReleaseFromHold
from .utils import verify_pin


class GrowerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grower
        fields = [
            'id', 'grower_id', 'grower_name', 'scheme',
            'area', 'group_name', 'manager', 'cy26_ha', 'contract_status',
        ]


class GrowerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grower
        fields = '__all__'


class TruckDeliverySerializer(serializers.ModelSerializer):
    difference = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True
    )

    class Meta:
        model = TruckDelivery
        fields = [
            'id', 'date_expected', 'area', 'transporter', 'truck_reg',
            'driver_name', 'driver_id', 'qty_booked', 'qty_offloaded',
            'difference', 'is_booked', 'created_by', 'created_by_username', 'created_at',
        ]
        read_only_fields = ['created_by', 'created_at']


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ['id', 'name', 'location']


class RejectionClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectionClassification
        fields = ['id', 'code', 'description']


class RejectedBaleSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    classification_code = serializers.CharField(source='classification.code', read_only=True)
    classification_description = serializers.CharField(source='classification.description', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = RejectedBale
        fields = [
            'id', 'date', 'floor', 'floor_name',
            'grower', 'grower_number', 'grower_name',
            'ticket_number', 'lot_number', 'group_number',
            'classification', 'classification_code', 'classification_description',
            'ntrm_type', 'created_by', 'created_by_username', 'created_at',
        ]
        read_only_fields = ['created_by', 'created_at']


class ReleaseFromHoldSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source='floor.name', read_only=True)
    floor_location = serializers.CharField(source='floor.location', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    bale_grower_name = serializers.CharField(source='rejected_bale.grower_name', read_only=True)
    bale_classification = serializers.CharField(source='rejected_bale.classification.code', read_only=True)

    class Meta:
        model = ReleaseFromHold
        fields = [
            'id', 'rejected_bale', 'ticket_number', 'resolution_date',
            'resolution', 'reference', 'floor', 'floor_name', 'floor_location',
            'bale_grower_name', 'bale_classification',
            'created_by', 'created_by_username', 'created_at',
        ]
        read_only_fields = ['created_by', 'created_at']


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
