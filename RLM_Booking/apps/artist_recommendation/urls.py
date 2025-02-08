from django.urls import path
from . import views
from .. import base_view

urlpatterns = [
    path('search-artist/', views.search_artist_route, name='search_artist_route'),
    path('get-events/', views.get_events_route, name='get_events_route'),

    path('', base_view.home.as_view(), name='home'),
    path('<path:path>', base_view.home.as_view()),
]
