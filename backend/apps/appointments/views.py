from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.appointments.models import Appointment
from apps.appointments.serializers import (
    AppointmentReadSerializer,
    AppointmentStatusUpdateSerializer,
    AppointmentWriteSerializer,
)
from apps.appointments.services import update_appointment_status


@api_view(['GET', 'POST'])
def appointment_list_create(request: Request) -> Response:
    """List all appointments or book a new appointment with transaction-safe conflict protection."""
    if request.method == 'GET':
        appointments = Appointment.objects.select_related('service').all()
        serializer = AppointmentReadSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        write_serializer = AppointmentWriteSerializer(data=request.data)
        if write_serializer.is_valid():
            try:
                with transaction.atomic():
                    appointment = write_serializer.save()
                read_serializer = AppointmentReadSerializer(appointment)
                return Response(read_serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {'detail': 'This service is already booked for the selected date and time.'},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(write_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def appointment_detail_delete(request: Request, pk: int) -> Response:
    """Retrieve or delete an appointment by ID."""
    appointment = get_object_or_404(Appointment.objects.select_related('service'), pk=pk)

    if request.method == 'GET':
        serializer = AppointmentReadSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
def appointment_status_update(request: Request, pk: int) -> Response:
    """Update appointment status following controlled state machine transition rules."""
    appointment = get_object_or_404(Appointment.objects.select_related('service'), pk=pk)

    serializer = AppointmentStatusUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_status = serializer.validated_data['status']
    updated_appointment = update_appointment_status(appointment, new_status)
    read_serializer = AppointmentReadSerializer(updated_appointment)
    return Response(read_serializer.data, status=status.HTTP_200_OK)
