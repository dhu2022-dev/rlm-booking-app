from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_management_page, name='event_management_page'),  
    path('search-events/', views.search_events, name='search_events'),
]
