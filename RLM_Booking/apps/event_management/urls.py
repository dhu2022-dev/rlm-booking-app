from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('api/save-event/', views.save_event, name='save_event'),
    path('api/get-events/', views.get_events, name='get_events'),
    path('api/delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
]
