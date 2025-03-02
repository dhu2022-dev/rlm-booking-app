from django.urls import path
from . import views
from .. import base_view

urlpatterns = [
    path('save-event/', views.save_event, name='save_event'),
    path('get-events/', views.get_events, name='get_events'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),

    path('', base_view.home.as_view(), name='home'),
]
