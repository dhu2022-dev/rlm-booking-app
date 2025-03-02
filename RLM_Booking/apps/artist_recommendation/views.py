from django.http import JsonResponse
from django.views.decorators.http import require_GET
from integrations.artist_event_search import get_spotify_token, search_artist, get_ticketmaster_events, analyze_local_global_events
from integrations.ticketmaster_api_manager import TicketmasterAPIManager
from shared_services.aws_data_manager import AWSDataManager
import os

# Initialize AWSDatabaseManager
db_manager = AWSDataManager(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('REGION_NAME'),
    table_name=os.getenv('TABLE_NAME')
)

# Initialize Ticketmaster API Manager
ticketmaster_manager = TicketmasterAPIManager()

# API endpoint for searching an artist
@require_GET
def search_artist_route(request):
    print("API hit successfully")
    artist_name = request.GET.get('name')
    cached_results = db_manager.get_cached_results(artist_name)

    if cached_results:
        print(f"Using cached results for {artist_name}")
        return JsonResponse(cached_results['data'], safe=False)

    token = get_spotify_token()
    artist_data = search_artist(artist_name, token)

    artists = artist_data.get('artists', {}).get('items', [artist_data])
    db_manager.cache_results(artist_name, artists)

    return JsonResponse(artists, safe=False)

# API endpoint for fetching upcoming events
@require_GET
def get_events_route(request):
    artist_name = request.GET.get('name')
    artist_popularity = request.GET.get('popularity', 50)
    target_country = request.GET.get('country', 'US')
    target_city = request.GET.get('city', 'Boston')
    postalcode = request.GET.get('postalcode', None)
    latitude = request.GET.get('latitude', None)
    longitude = request.GET.get('longitude', None)
    radius = request.GET.get('radius', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    try:
        # Fetch events using the refactored method
        events = ticketmaster_manager.fetch_events(
            artist=artist_name,
            postalcode=postalcode,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            radius=int(radius) if radius else None,
            start_date=start_date,
            end_date=end_date
        )

        if events:
            local_events, global_events = analyze_local_global_events(events, target_country, target_city)

            # Add additional metadata (e.g., suggested price, predicted sales)
            for event in events:
                event['predicted_sales'] = 10000  # Placeholder, replace with ML model logic
                event['suggested_price'] = 50

            return JsonResponse({
                'events': events,
                'local_event_count': len(local_events),
                'global_event_count': len(global_events),
                'local_events': local_events,
                'global_events': global_events
            })

    except Exception as e:
        print("something wrong calling ticketmaster class")
        #logger.error(f"Error fetching events: {str(e)}", exc_info=True)

    return JsonResponse({
        'events': [],
        'local_event_count': 0,
        'global_event_count': 0,
        'local_events': [],
        'global_events': []
    })