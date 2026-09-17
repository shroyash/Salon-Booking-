from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from apps.services.models import Service
from apps.services.serializers import ServiceSerializer


@api_view(['GET', 'POST'])
def service_list_create(request: Request) -> Response:
    """List all active salon services or create a new service."""
    if request.method == 'GET':
        services = Service.objects.filter(is_active=True)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def service_detail_update_delete(request: Request, pk: int) -> Response:
    """Retrieve, update, or delete a salon service by ID."""
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'GET':
        serializer = ServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = ServiceSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            # If service has related appointments or is protected, fallback to soft deletion
            if hasattr(service, 'appointments') and service.appointments.exists():
                service.is_active = False
                service.save()
            else:
                service.delete()
        except ProtectedError:
            service.is_active = False
            service.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
