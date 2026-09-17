from decimal import Decimal
from unittest.mock import patch
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.appointments.models import Appointment, AppointmentStatus
from apps.services.models import Service


class AppointmentAPITests(APITestCase):
    """Unit test suite for Appointment domain API endpoints."""

    def setUp(self) -> None:
        self.service1 = Service.objects.create(
            name='Haircut',
            price=Decimal('500.00'),
            duration_minutes=30
        )
        self.service2 = Service.objects.create(
            name='Facial',
            price=Decimal('1500.00'),
            duration_minutes=60
        )

        self.list_create_url = reverse('appointments:appointment-list-create')
        self.valid_payload = {
            'customer_name': 'Ram Sharma',
            'customer_phone': '9841000000',
            'service': self.service1.id,
            'appointment_date': '2026-10-15',
            'appointment_time': '10:00:00',
            'notes': 'Please keep it short.',
        }

    def test_valid_appointment_creation(self) -> None:
        """Verify successful creation of a valid appointment returns 201 Created."""
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer_name'], 'Ram Sharma')
        self.assertEqual(response.data['customer_phone'], '9841000000')
        self.assertEqual(response.data['service']['id'], self.service1.id)
        self.assertEqual(response.data['appointment_date'], '2026-10-15')
        self.assertEqual(response.data['appointment_time'], '10:00:00')
        self.assertEqual(response.data['notes'], 'Please keep it short.')

    def test_missing_customer_name(self) -> None:
        """Verify appointment creation fails when customer_name is missing."""
        payload = {**self.valid_payload}
        del payload['customer_name']
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_name', response.data)

    def test_whitespace_only_customer_name(self) -> None:
        """Verify appointment creation fails when customer_name contains only whitespace."""
        payload = {**self.valid_payload, 'customer_name': '   '}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_name', response.data)

    def test_missing_phone(self) -> None:
        """Verify appointment creation fails when customer_phone is missing."""
        payload = {**self.valid_payload}
        del payload['customer_phone']
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('customer_phone', response.data)

    def test_missing_service(self) -> None:
        """Verify appointment creation fails when service is missing."""
        payload = {**self.valid_payload}
        del payload['service']
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service', response.data)

    def test_invalid_service_id(self) -> None:
        """Verify appointment creation fails when service ID does not exist."""
        payload = {**self.valid_payload, 'service': 99999}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('service', response.data)

    def test_missing_date(self) -> None:
        """Verify appointment creation fails when appointment_date is missing."""
        payload = {**self.valid_payload}
        del payload['appointment_date']
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('appointment_date', response.data)

    def test_missing_time(self) -> None:
        """Verify appointment creation fails when appointment_time is missing."""
        payload = {**self.valid_payload}
        del payload['appointment_time']
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('appointment_time', response.data)

    def test_valid_notes_optional(self) -> None:
        """Verify appointment creation works without notes or with empty notes."""
        payload = {**self.valid_payload, 'notes': ''}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['notes'], '')

    def test_appointment_defaults_to_pending(self) -> None:
        """Verify newly created appointment defaults to PENDING status."""
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], AppointmentStatus.PENDING)
        self.assertEqual(response.data['status_label'], 'Pending')

    def test_duplicate_same_service_date_time_is_rejected(self) -> None:
        """Verify booking same service at same date and time returns 409 Conflict."""
        first_response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        duplicate_payload = {
            **self.valid_payload,
            'customer_name': 'Sita Thapa',
            'customer_phone': '9841999999',
        }
        second_response = self.client.post(self.list_create_url, duplicate_payload)
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            second_response.data['detail'],
            'This service is already booked for the selected date and time.'
        )

    def test_different_service_at_same_date_time_is_allowed(self) -> None:
        """Verify booking different service at same date and time is allowed."""
        self.client.post(self.list_create_url, self.valid_payload)
        different_service_payload = {
            **self.valid_payload,
            'customer_name': 'Gita Roy',
            'service': self.service2.id,
        }
        response = self.client.post(self.list_create_url, different_service_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_same_service_at_different_time_is_allowed(self) -> None:
        """Verify booking same service at a different time is allowed."""
        self.client.post(self.list_create_url, self.valid_payload)
        different_time_payload = {
            **self.valid_payload,
            'customer_name': 'Hari KC',
            'appointment_time': '11:00:00',
        }
        response = self.client.post(self.list_create_url, different_time_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_same_service_on_different_date_is_allowed(self) -> None:
        """Verify booking same service on a different date is allowed."""
        self.client.post(self.list_create_url, self.valid_payload)
        different_date_payload = {
            **self.valid_payload,
            'customer_name': 'Bikash Rana',
            'appointment_date': '2026-10-16',
        }
        response = self.client.post(self.list_create_url, different_date_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('apps.appointments.serializers.AppointmentWriteSerializer.save')
    def test_integrity_error_concurrency_fallback_returns_409(self, mock_save) -> None:
        """Verify DB IntegrityError from race condition returns 409 Conflict."""
        mock_save.side_effect = IntegrityError("UNIQUE constraint failed")
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data['detail'],
            'This service is already booked for the selected date and time.'
        )

    def test_deleting_nonexistent_appointment_returns_404(self) -> None:
        """Verify DELETE on non-existent appointment ID returns 404 Not Found."""
        url = reverse('appointments:appointment-detail', kwargs={'pk': 99999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_appointment_deletion(self) -> None:
        """Verify DELETE on an existing appointment deletes it and returns 204 No Content."""
        create_res = self.client.post(self.list_create_url, self.valid_payload)
        appointment_id = create_res.data['id']
        url = reverse('appointments:appointment-detail', kwargs={'pk': appointment_id})

        del_res = self.client.delete(url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Appointment.objects.filter(pk=appointment_id).exists())


class AppointmentStatusTransitionAPITests(APITestCase):
    """Unit test suite for controlled Appointment status transitions."""

    def setUp(self) -> None:
        self.service = Service.objects.create(
            name='Haircut',
            price=Decimal('500.00'),
            duration_minutes=30
        )
        self.appointment = Appointment.objects.create(
            customer_name='Ram Sharma',
            customer_phone='9841000000',
            service=self.service,
            appointment_date='2026-10-15',
            appointment_time='10:00:00',
            status=AppointmentStatus.PENDING
        )
        self.status_url = reverse(
            'appointments:appointment-status-update',
            kwargs={'pk': self.appointment.pk}
        )

    def test_allowed_transition_pending_to_confirmed(self) -> None:
        """Verify PENDING -> CONFIRMED transition succeeds (200 OK)."""
        response = self.client.patch(self.status_url, {'status': AppointmentStatus.CONFIRMED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], AppointmentStatus.CONFIRMED)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, AppointmentStatus.CONFIRMED)

    def test_allowed_transition_pending_to_cancelled(self) -> None:
        """Verify PENDING -> CANCELLED transition succeeds (200 OK)."""
        response = self.client.patch(self.status_url, {'status': AppointmentStatus.CANCELLED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], AppointmentStatus.CANCELLED)

    def test_allowed_transition_confirmed_to_completed(self) -> None:
        """Verify CONFIRMED -> COMPLETED transition succeeds (200 OK)."""
        self.appointment.status = AppointmentStatus.CONFIRMED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.COMPLETED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], AppointmentStatus.COMPLETED)

    def test_allowed_transition_confirmed_to_cancelled(self) -> None:
        """Verify CONFIRMED -> CANCELLED transition succeeds (200 OK)."""
        self.appointment.status = AppointmentStatus.CONFIRMED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.CANCELLED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], AppointmentStatus.CANCELLED)

    def test_invalid_transition_pending_to_completed(self) -> None:
        """Verify PENDING -> COMPLETED transition fails (400 Bad Request)."""
        response = self.client.patch(self.status_url, {'status': AppointmentStatus.COMPLETED})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            'Cannot transition an appointment from PENDING to COMPLETED.'
        )

    def test_invalid_transition_completed_to_pending(self) -> None:
        """Verify COMPLETED -> PENDING transition fails (400 Bad Request)."""
        self.appointment.status = AppointmentStatus.COMPLETED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.PENDING})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            'Cannot transition an appointment from COMPLETED to PENDING.'
        )

    def test_invalid_transition_completed_to_cancelled(self) -> None:
        """Verify COMPLETED -> CANCELLED transition fails (400 Bad Request)."""
        self.appointment.status = AppointmentStatus.COMPLETED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.CANCELLED})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_transition_cancelled_to_confirmed(self) -> None:
        """Verify CANCELLED -> CONFIRMED transition fails (400 Bad Request)."""
        self.appointment.status = AppointmentStatus.CANCELLED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.CONFIRMED})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_transition_cancelled_to_completed(self) -> None:
        """Verify CANCELLED -> COMPLETED transition fails (400 Bad Request)."""
        self.appointment.status = AppointmentStatus.CANCELLED
        self.appointment.save()

        response = self.client.patch(self.status_url, {'status': AppointmentStatus.COMPLETED})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_status_update_is_rejected(self) -> None:
        """Verify updating to the same status is rejected as an invalid transition (400 Bad Request)."""
        response = self.client.patch(self.status_url, {'status': AppointmentStatus.PENDING})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['detail'],
            'Cannot transition an appointment from PENDING to PENDING.'
        )

    def test_invalid_status_value_returns_400(self) -> None:
        """Verify providing an unknown status choice returns 400 Bad Request."""
        response = self.client.patch(self.status_url, {'status': 'INVALID_STATUS'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_nonexistent_appointment_returns_404(self) -> None:
        """Verify status update on non-existent appointment ID returns 404 Not Found."""
        url = reverse('appointments:appointment-status-update', kwargs={'pk': 99999})
        response = self.client.patch(url, {'status': AppointmentStatus.CONFIRMED})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
