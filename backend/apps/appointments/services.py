from rest_framework import status
from rest_framework.exceptions import APIException
from apps.appointments.models import Appointment, AppointmentStatus


class InvalidStatusTransitionError(APIException):
    """Exception raised when an invalid appointment status transition is requested."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_status_transition'

    def __init__(self, current_status: str, new_status: str) -> None:
        detail = f"Cannot transition an appointment from {current_status} to {new_status}."
        super().__init__(detail=detail)


ALLOWED_TRANSITIONS = {
    AppointmentStatus.PENDING: {
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED,
    },
    AppointmentStatus.CONFIRMED: {
        AppointmentStatus.COMPLETED,
        AppointmentStatus.CANCELLED,
    },
    AppointmentStatus.COMPLETED: set(),  # Terminal state
    AppointmentStatus.CANCELLED: set(),  # Terminal state
}


def update_appointment_status(appointment: Appointment, new_status: str) -> Appointment:
    """
    Validates and performs an appointment status transition according to domain business rules.

    Allowed transitions:
    - PENDING -> CONFIRMED, CANCELLED
    - CONFIRMED -> COMPLETED, CANCELLED
    - COMPLETED -> None (Terminal)
    - CANCELLED -> None (Terminal)

    Raises InvalidStatusTransitionError if the transition is illegal or redundant.
    """
    current_status = appointment.status

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidStatusTransitionError(current_status, new_status)

    appointment.status = new_status
    appointment.save(update_fields=['status', 'updated_at'])
    return appointment
