from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """Configuration for the appointments domain application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    label = 'appointments'
