from django.urls import path
from apps.appointments.views import (
    appointment_detail_delete,
    appointment_list_create,
    appointment_status_update,
)

app_name = 'appointments'

urlpatterns = [
    path('', appointment_list_create, name='appointment-list-create'),
    path('<int:pk>/', appointment_detail_delete, name='appointment-detail'),
    path('<int:pk>/status/', appointment_status_update, name='appointment-status-update'),
]
