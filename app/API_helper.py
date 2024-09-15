import requests
import base64
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, TICKETMASTER_API_KEY

# Get Spotify Access Token
def get_spotify_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_headers = {
        'Authorization': 'Basic ' + base64.b64encode((SPOTIFY_CLIENT_ID + ':' + SPOTIFY_CLIENT_SECRET).encode()).decode(),
    }
    auth_data = {'grant_type': 'client_credentials'}
    res = requests.post(auth_url, headers=auth_headers, data=auth_data)
    return res.json()['access_token']

# Search for artist on Spotify
def search_artist(artist_name, token):
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json()

# Get artist events from Ticketmaster
def get_ticketmaster_events(artist_name):
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?keyword={artist_name}&apikey={TICKETMASTER_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch events'}

#adjust the target_country and target_city in the analyze_local_global_events function to fit the actual location of the venue you're targeting.
def analyze_local_global_events(events, target_country=None, target_city=None):
    local_events = []
    global_events = []
    country_mapping = {
        "US": ["US", "United States", "USA", "America", "United States of America", "The United States of America"],
        "UK": ["UK", "United Kingdom", "Britain", "England", "Great Britain"],
        "Canada": ["Canada", "CA", "The Great White North"],
        "Australia": ["Australia", "AU", "Oz", "Down Under"],
        "Germany": ["Germany", "DE", "Deutschland"],
        "France": ["France", "FR", "La Belle France"],
        "Italy": ["Italy", "IT", "Italia"],
        "Spain": ["Spain", "ES", "España"],
        "Brazil": ["Brazil", "BR", "Brasil"],
        "Mexico": ["Mexico", "MX", "México"],
        "India": ["India", "IN", "Bharat"],
        "China": ["China", "CN", "中华人民共和国"],
        "Japan": ["Japan", "JP", "日本"],
        "South Korea": ["South Korea", "KR", "대한민국"],
        "Russia": ["Russia", "RU", "Россия"],
        "South Africa": ["South Africa", "ZA", "Republic of South Africa"],
        "Argentina": ["Argentina", "AR"],
        "Chile": ["Chile", "CL"],
        "Colombia": ["Colombia", "CO"],
        "Saudi Arabia": ["Saudi Arabia", "SA", "KSA"],
        "United Arab Emirates": ["United Arab Emirates", "UAE", "الإمارات العربية المتحدة"],
        "Turkey": ["Turkey", "TR", "Türkiye"]
        # Add more mappings as needed
    }



    # Normalize and map target country
    normalized_target_country = target_country.strip().lower() if target_country else None
    mapped_target_country = None

    if normalized_target_country:
        print("Normalized target country: " + normalized_target_country)
        for country, aliases in country_mapping.items():
            if normalized_target_country in [name.lower() for name in aliases]:
                mapped_target_country = country
                break

    for event in events:
        # Extract venue data
        venue = event.get('_embedded', {}).get('venues', [{}])[0]  # Safely get the first venue
        event_country = venue.get('country', {}).get('name', None)  # Get country name
        event_city = venue.get('city', {}).get('name', None)  # Get city name

        # Skip events with missing country or city
        if event_country is None or event_city is None:
            continue

        # Normalize and map event country
        normalized_event_country = event_country.strip().lower() if event_country else None
        mapped_event_country = None

        if normalized_event_country:
            print("Normalized event country: " + normalized_event_country)
            for country, aliases in country_mapping.items():
                if normalized_event_country in [name.lower() for name in aliases]:
                    mapped_event_country = country
                    break

        # Normalize event city
        normalized_event_city = event_city.strip().lower() if event_city else None
        normalized_target_city = target_city.strip().lower() if target_city else None

        # Log values for debugging
        print(f"Event Country: {mapped_event_country}, Target Country: {mapped_target_country}")
        print(f"Event City: {normalized_event_city}, Target City: {normalized_target_city}")

        # Check if the event is in the target country and city (if specified)
        if mapped_event_country == mapped_target_country:
            if normalized_event_city == normalized_target_city:
                local_events.append(event)
            else:
                global_events.append(event)
        elif normalized_event_city == normalized_target_city:
            local_events.append(event)
        else:
            global_events.append(event)

    return local_events, global_events


 
