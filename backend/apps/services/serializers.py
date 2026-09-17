from decimal import Decimal
from rest_framework import serializers
from apps.services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model handling string normalization and numeric validation."""

    is_active = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'price',
            'duration_minutes',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Name cannot be empty or contain only whitespace.')
        return value.strip()

    def validate_price(self, value: Decimal) -> Decimal:
        if value <= Decimal('0.00'):
            raise serializers.ValidationError('Price must be greater than zero.')
        return value

    def validate_duration_minutes(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError('Duration must be greater than zero.')
        return value
