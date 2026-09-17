from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from apps.appointments.models import Appointment, AppointmentStatus
from apps.services.serializers import ServiceSerializer


class SlotConflictError(APIException):
    """Custom API exception returning HTTP 409 Conflict when a booking slot is unavailable."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This service is already booked for the selected date and time.'
    default_code = 'slot_conflict'


class AppointmentWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Appointment instances."""

    notes = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer_name',
            'customer_phone',
            'service',
            'appointment_date',
            'appointment_time',
            'notes',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
        validators = []

    def validate_customer_name(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Customer name cannot be empty or contain only whitespace.')
        return value.strip()

    def validate_customer_phone(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError('Customer phone cannot be empty or contain only whitespace.')
        return value.strip()

    def validate(self, attrs: dict) -> dict:
        service = attrs.get('service')
        appointment_date = attrs.get('appointment_date')
        appointment_time = attrs.get('appointment_time')

        if service and appointment_date and appointment_time:
            query = Appointment.objects.filter(
                service=service,
                appointment_date=appointment_date,
                appointment_time=appointment_time
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)

            if query.exists():
                raise SlotConflictError('This service is already booked for the selected date and time.')

        return attrs


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    """Serializer for validating appointment status PATCH request payload."""

    status = serializers.ChoiceField(choices=AppointmentStatus.choices)


class AppointmentReadSerializer(serializers.ModelSerializer):
    """Serializer for reading Appointment instances with embedded service details."""

    service = ServiceSerializer(read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'customer_name',
            'customer_phone',
            'service',
            'appointment_date',
            'appointment_time',
            'notes',
            'status',
            'status_label',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
