from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME, TABLE_NAME
from flask import Blueprint, render_template, request, jsonify
from .API_helper import get_spotify_token, search_artist, get_ticketmaster_events, analyze_local_global_events
from .AWSDatabase_manager import AWSDatabaseManager
from .Model.recommendation_engine import call_azure_ml_model, predict_ticket_sales
#from .Model.recommendation_engine import predict_ticket_sales, suggest_ticket_price
import json

main = Blueprint('main', __name__)

# Initialize the AWSDatabaseManager instance
db_manager = AWSDatabaseManager(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION_NAME,
    table_name=TABLE_NAME
)
# Route to serve the homepage
@main.route('/')
def home():
    return render_template('index.html')

# Route to search for an artist via Spotify
@main.route('/search-artist', methods=['GET'])
def search_artist_route():
    artist_name = request.args.get('name')

    # Check if results are cached in DynamoDB
    cached_results = db_manager.get_cached_results(artist_name)
    if cached_results:
        print(f"Using cached results for {artist_name}")
        return jsonify(cached_results['data'])  # No need to use json.loads

    # If no cache, fetch a new token and search the artist
    token = get_spotify_token()
    print("Token is: " + token)
    artist_data = search_artist(artist_name, token)

    if 'artists' in artist_data:
        artists = artist_data['artists']['items']
    else:
        artists = [artist_data]

    # Cache the new results in DynamoDB
    db_manager.cache_results(artist_name, artists)

    return jsonify(artists)

# Route to fetch events from Ticketmaster
@main.route('/get-events', methods=['GET'])
def get_events_route():
    artist_name = request.args.get('name')
    artist_popularity = request.args.get('popularity', 50)  # Default popularity value
    target_country = request.args.get('country', 'US')  # Default country value
    target_city = request.args.get('city', '')  # Default city value

    print(f"Fetching events for artist: {artist_name}")
    print(f"Country: {target_country}, City: {target_city}")

    # Your function to fetch events
    events_data = get_ticketmaster_events(artist_name)
    
    # Check if events_data contains '_embedded' and 'events'
    if events_data and '_embedded' in events_data and 'events' in events_data['_embedded']:
        events = events_data['_embedded']['events']
        print(f"Number of events retrieved: {len(events)}")

        if not events:
            return jsonify({
                'events': [],
                'local_event_count': 0,
                'global_event_count': 0,
                'local_events': [],
                'global_events': []
            })

        local_events, global_events = analyze_local_global_events(events, target_country=target_country, target_city=target_city)
        
        # Calculate and add additional data to each event
        for event in events:
            if '_embedded' in event and 'venues' in event['_embedded']:
                venue_capacity = event['_embedded']['venues'][0].get('capacity', 5000)  # Default capacity
                predicted_sales = predict_ticket_sales(int(artist_popularity), venue_capacity)
                suggested_price = call_azure_ml_model(artist_name) #suggest_ticket_price(predicted_sales, venue_capacity)
                
                event['predicted_sales'] = predicted_sales
                event['suggested_price'] = suggested_price

        return jsonify({
            'events': events,
            'local_event_count': len(local_events),
            'global_event_count': len(global_events),
            'local_events': local_events,
            'global_events': global_events
        })
    
    # Return an empty list and counts if events data is not properly structured
    return jsonify({
        'events': [],
        'local_event_count': 0,
        'global_event_count': 0,
        'local_events': [],
        'global_events': []
    })