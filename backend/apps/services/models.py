from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models


class Service(models.Model):
    """Model representing a salon service available for customer booking."""

    name = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gt=Decimal('0.00')),
                name='service_price_gt_zero'
            ),
            models.CheckConstraint(
                check=models.Q(duration_minutes__gt=0),
                name='service_duration_gt_zero'
            ),
        ]

    def clean(self) -> None:
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValidationError({'name': 'Name cannot be empty or contain only whitespace.'})
        if self.price is not None and self.price <= Decimal('0.00'):
            raise ValidationError({'price': 'Price must be greater than zero.'})
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise ValidationError({'duration_minutes': 'Duration must be greater than zero.'})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes} mins) - NPR {self.price}"
