from django.core.exceptions import ValidationError
from django.db import models
from apps.services.models import Service


class AppointmentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Appointment(models.Model):
    """Model representing a customer appointment booking for a salon service."""

    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        constraints = [
            models.UniqueConstraint(
                fields=['service', 'appointment_date', 'appointment_time'],
                name='unique_service_appointment_slot'
            )
        ]
        indexes = [
            models.Index(fields=['appointment_date', 'appointment_time']),
            models.Index(fields=['status']),
        ]

    def clean(self) -> None:
        if self.customer_name is not None:
            self.customer_name = self.customer_name.strip()
            if not self.customer_name:
                raise ValidationError({'customer_name': 'Customer name cannot be empty or contain only whitespace.'})
        if self.customer_phone is not None:
            self.customer_phone = self.customer_phone.strip()
            if not self.customer_phone:
                raise ValidationError({'customer_phone': 'Customer phone cannot be empty or contain only whitespace.'})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.customer_name} - {self.service.name} on {self.appointment_date} at {self.appointment_time} ({self.status})"
