from django.urls import path
from apps.services.views import service_detail_update_delete, service_list_create

app_name = 'services'

urlpatterns = [
    path('', service_list_create, name='service-list-create'),
    path('<int:pk>/', service_detail_update_delete, name='service-detail'),
]
