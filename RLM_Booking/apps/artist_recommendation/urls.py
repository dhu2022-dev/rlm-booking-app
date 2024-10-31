from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search-artist/', views.search_artist_route, name='search_artist_route'),
    path('get-events/', views.get_events_route, name='get_events_route'),
]
