from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.services.models import Service


class ServiceAPITests(APITestCase):
    """Unit tests for Service domain API endpoints."""

    def setUp(self) -> None:
        self.list_create_url = reverse('services:service-list-create')
        self.valid_payload = {
            'name': 'Haircut',
            'price': '500.00',
            'duration_minutes': 30,
        }

    def test_valid_service_creation(self) -> None:
        """Verify successful creation of a valid service returns 201 Created."""
        response = self.client.post(self.list_create_url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Haircut')
        self.assertEqual(Decimal(response.data['price']), Decimal('500.00'))
        self.assertEqual(response.data['duration_minutes'], 30)
        self.assertTrue(response.data['is_active'])
        self.assertTrue(Service.objects.filter(name='Haircut').exists())

    def test_empty_name_validation(self) -> None:
        """Verify service creation with empty name fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'name': ''}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_whitespace_only_name_validation(self) -> None:
        """Verify service creation with whitespace-only name fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'name': '   '}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_zero_price_validation(self) -> None:
        """Verify service creation with zero price fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'price': '0.00'}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_negative_price_validation(self) -> None:
        """Verify service creation with negative price fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'price': '-150.00'}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_zero_duration_validation(self) -> None:
        """Verify service creation with zero duration fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'duration_minutes': 0}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration_minutes', response.data)

    def test_negative_duration_validation(self) -> None:
        """Verify service creation with negative duration fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'duration_minutes': -20}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('duration_minutes', response.data)

    def test_invalid_type_payload_validation(self) -> None:
        """Verify non-numeric price or duration fails with 400 Bad Request."""
        payload = {**self.valid_payload, 'price': 'invalid', 'duration_minutes': 'abc'}
        response = self.client.post(self.list_create_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('duration_minutes', response.data)

    def test_successful_service_list(self) -> None:
        """Verify GET /api/services/ returns only active services."""
        Service.objects.create(name='Facial', price=Decimal('1500.00'), duration_minutes=60, is_active=True)
        Service.objects.create(name='Old Service', price=Decimal('100.00'), duration_minutes=15, is_active=False)

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Facial')

    def test_successful_service_detail_retrieval(self) -> None:
        """Verify GET /api/services/:id/ returns single service details with 200 OK."""
        service = Service.objects.create(name='Facial', price=Decimal('1500.00'), duration_minutes=60)
        url = reverse('services:service-detail', kwargs={'pk': service.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], service.pk)
        self.assertEqual(response.data['name'], 'Facial')

    def test_successful_update(self) -> None:
        """Verify PUT /api/services/:id/ updates fields correctly."""
        service = Service.objects.create(name='Facial', price=Decimal('1500.00'), duration_minutes=60)
        url = reverse('services:service-detail', kwargs={'pk': service.pk})
        update_payload = {
            'name': 'Premium Facial',
            'price': '2000.00',
            'duration_minutes': 75,
            'is_active': True,
        }
        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Premium Facial')
        self.assertEqual(Decimal(response.data['price']), Decimal('2000.00'))
        self.assertEqual(response.data['duration_minutes'], 75)

    def test_nonexistent_service_returns_404(self) -> None:
        """Verify operations on a non-existent service ID return 404 Not Found."""
        url = reverse('services:service-detail', kwargs={'pk': 99999})
        get_res = self.client.get(url)
        put_res = self.client.put(url, self.valid_payload)
        del_res = self.client.delete(url)

        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(put_res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(del_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_deletion(self) -> None:
        """Verify DELETE /api/services/:id/ deletes service and returns 204 No Content."""
        service = Service.objects.create(name='Temporary Service', price=Decimal('300.00'), duration_minutes=20)
        url = reverse('services:service-detail', kwargs={'pk': service.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Service.objects.filter(pk=service.pk).exists())
