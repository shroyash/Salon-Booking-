from django.contrib import admin
from django.urls import include, path
from apps.common.views import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/services/', include('apps.services.urls', namespace='services')),
    path('api/appointments/', include('apps.appointments.urls', namespace='appointments')),
]
