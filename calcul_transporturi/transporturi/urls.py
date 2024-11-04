from django.urls import path
from .views import add_transport, edit_transport,export_data, transport_detail,transport_history, view_transports,mark_as_departed,view_vehicle_types,add_vehicle_type,update_transport_status,request_transport_status,mark_transport_as_completed,upload_transport_file

urlpatterns = [
    path('transports/', view_transports, name='view_transports'),
    path('transports/add/', add_transport, name='add_transport'),
    path('transports/edit/<int:transport_id>/', edit_transport, name='modify_transport'),
    path('view_transports/transport/mark_departed/<int:transport_id>/', mark_as_departed, name='mark_as_departed'),
    path('transports/add_vehicle_type/', add_vehicle_type, name='add_vehicle_type'),
    path('transports/view_vehicle_types/', view_vehicle_types, name='view_vehicle_types'),
    path('request_transport_status/<int:transport_id>/', request_transport_status, name='request_transport_status'),
    path('mark_transport_as_completed/<int:transport_id>/', mark_transport_as_completed, name='mark_transport_as_completed'),
    path('update_transport_status/<int:transport_id>/', update_transport_status, name='update_transport_status'),
    path('transports/<int:transport_id>/detail/', transport_detail, name='transport_detail'),
    path('transports/<int:transport_id>/history/', transport_history, name='transport_history'),
    path('transports/export/', export_data, name='export_data'),
    path('transport/upload/<int:transport_id>/', upload_transport_file, name='upload_transport_file'),
]
