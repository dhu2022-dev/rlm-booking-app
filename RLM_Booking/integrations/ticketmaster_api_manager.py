import os
from dotenv import load_dotenv
from .api_manager import APIManager
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)
load_dotenv()
TICKETMASTER_API_KEY = os.getenv('TICKETMASTER_API_KEY')

class TicketmasterAPIManager(APIManager):
    """
    The API provides access to content sourced from various platforms, including Ticketmaster, Universe, FrontGate Tickets and Ticketmaster Resale (TMR).
    API Limits:
    - The default quota is 5000 API calls per day and rate limitation of 5 requests per second.
    - Deep Paging: Ticketmaster only supports retrieving the 1000th item. i.e. ( size * page < 1000)

    Endpoints (also the types of data):
    - An *event* is the central entity to which all other entities relate. An event is basically a happening at a particular date and time.
    - An *attraction* is the artist, team or the performers at the event.
    - A *classification* is an attribute of both events and attractions and has three different levels:
        - Segment: This could be music, sports, arts & theater, family, Film, and miscellaneous.
        - Genre: These are the various genres under each segment.
        - Sub-genre: The secondary genre for this event or attraction under this particular segment.
    - A *venue* describes the physical location at which the event is taking place.
    """

    # Base URL for Discovery API. Other partner only APIs if needed on ticketmaster site.
    TICKETMASTER_BASE_URL = 'https://app.ticketmaster.com/discovery/v2/'

    def __init__(self):
        """
        Initializes the TicketmasterAPIManager with the necessary credentials and base URL.
        """
        credentials = {
            'apikey': TICKETMASTER_API_KEY
        }
        super().__init__(
            base_url=self.TICKETMASTER_BASE_URL,
            auth_type='APIKey',
            credentials=credentials
        )

    def fetch_ID(self, item_type: str, item_name: str) -> str:
        """
        Get the Ticketmaster API ID for a specific item based on its type and name.

        Args:
            item_type (str): The type of item (artist, event, venue).
            item_name (str): The name of the item. Must match exactly.

        Returns:
            str: The unique identifier (id) of the item, or an empty string if not found.
        """
        logger.info(f"Fetching ID for {item_type} '{item_name}'")
        endpoint_map = {
            'artist': 'attractions',
            'event': 'events',
            'venue': 'venues',
        }
        if item_type not in endpoint_map:
            logger.warning(f"Unsupported item type: {item_type}")
            return ''

        category = endpoint_map[item_type]
        params = {
            'keyword': item_name
        }
        logger.debug(f"Final API parameters: {params}")
        response = self.make_request(endpoint=category, params=params)

        # Log the raw response for debugging
        logger.debug(f"API Response for {item_type} '{item_name}': {response}")

        # Validate the response structure
        if not response or '_embedded' not in response or category not in response['_embedded']:
            logger.warning(f"No {item_type} found for name: {item_name}")
            return ''

        # Handle list response
        items = response['_embedded'][category]
        if isinstance(items, list):
            for item in items:
                if 'id' in item:
                    logging.info(f"Found {item_type} ID: {item['id']} for {item_name}")
                    return item['id']
            logger.warning(f"No ID found in {item_type} list for name: {item_name}")
        else:
            logger.warning(f"Unexpected structure for {item_type}: {items}")

        return ''

    
    def fetch_events(self, 
                 artist: Optional[str] = None, 
                 #genre: Optional[str] = None, 
                 postalcode: Optional[str] = None, 
                 latitude: Optional[float] = 0.0,
                 longitude: Optional[float] = 0.0,
                 radius: Optional[int] = None, 
                 start_date: Optional[str] = None, 
                 end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for events based on a combination of parameters. 
        We use id over name when possible for more accurate results.

        Args:
            artist (Optional[str]): The name of the artist.
            #genre (Optional[str]): The genre of the event.
            postalcode (Optional[str]): The postal code to search within.
            latitude (Optional[float]): The latitude for geographic search.
            longitude (Optional[float]): The longitude for geographic search.
            radius (Optional[int]): The radius in miles to search within.
            start_date (Optional[str]): The start date in the format 'YYYY-MM-DD'.
            end_date (Optional[str]): The end date in the format 'YYYY-MM-DD'.

        Returns:
            list: A list of parsed event JSON objects.
        """
        logger.info("Fetching events from Ticketmaster API")
        endpoint = 'events'
        params = {}

        if artist:
            artist_id = self.fetch_ID('artist', artist)
            if artist_id:
                params['attractionId'] = artist_id
        # if genre:
        #     params['classificationName'] = genre
        if postalcode:
            params['postalCode'] = postalcode
        if latitude and longitude:
            params['latlong'] = f"{latitude},{longitude}"
        if radius:
            params['radius'] = radius
            params['unit'] = 'miles'
        if start_date:
            params['startDateTime'] = f"{start_date}T05:00:00Z" #last part ot encode date to ISO, midnight UTC --> 5am local time
        if end_date:
            params['endDateTime'] = f"{end_date}T04:59:59Z"

        logger.debug(f"Final API parameters: {params}")

        try:
            response = self.make_request(endpoint=endpoint, params=params)
            logger.debug(f"Raw API response: {response}")

            if response and '_embedded' in response and 'events' in response['_embedded']:
                events = response['_embedded']['events']
                parsed_events = [self.fetch_event_details(event=event) for event in events]
                return parsed_events
            logger.info("No events found in the API response.")
            return []
        except Exception as e:
            logger.error(f"Error while fetching events: {str(e)}", exc_info=True)
            raise

    def fetch_event_details(self, event_id: Optional[str] = None, event: Optional[Dict[str, Any]] = None) -> dict:
        """
        Get details for a specific event using its unique identifier or parse an event JSON object.

        Args:
            event_id (Optional[str]): The unique identifier for the event.
            event (Optional[Dict[str, Any]]): The event JSON object.

        Returns:
            dict: A dictionary containing the relevant event details.
        """
        logger.info(f"Fetching details for event with ID: {event_id}")
        if event is None:
            if event_id is None:
                logger.warning("No event_id or event JSON object provided.")
                return {}
            endpoint = f'events/{event_id}'
            response = self.make_request(endpoint=endpoint)
            
            if not response:
                logger.warning(f"No details found for event with id: {event_id}")
                return {}
            event = response

        event_details = {
            'name': event.get('name'),
            'id': event.get('id'),
            'url': event.get('url'),
            'locale': event.get('locale'),
            'description': event.get('description'),
            'additionalInfo': event.get('additionalInfo'),
            'images': event.get('images', []),
            'dates': event.get('dates', {}),
            'sales': event.get('sales', {}),
            'priceRanges': event.get('priceRanges', []),
            'classifications': event.get('classifications', []),
            'location': event.get('location', {}),
            'distance': event.get('distance'),
            'units': event.get('units')
        }

        return event_details

    def fetch_artist_details(self, artist_id: str) -> dict:
        """
        Get details for a specific attraction using its unique identifier.

        Args:
            attraction_id (str): The unique identifier for the attraction.

        Returns:
            dict: A dictionary containing the (relevant) attraction details.
        """
        logger.info(f"Fetching details for artist with ID: {artist_id}")

        endpoint = f'attractions/{artist_id}'
        response = self.make_request(endpoint=endpoint)
        
        if not response:
            logger.warning(f"No details found for artist with id: {artist_id}")
            return {}

        artist_details = {
            'name': response.get('name'),
            'id': response.get('id'),
            'description': response.get('description'),
            'additionalInfo': response.get('additionalInfo'),
            'url': response.get('url'),
            'classifications': response.get('classifications', []),
            'numUpcomingEvents': response.get('upcomingEvents', '')
        }

        return artist_details

    def fetch_venue_details(self, venue_id: str) -> dict:
        """
        Get details for a specific venue using its unique identifier.

        Args:
            venue_id (str): The unique identifier for the venue.

        Returns:
            dict: A dictionary containing the venue details.
        """
        logger.info(f"Fetching details for venue with ID: {venue_id}")
        
        endpoint = f'venues/{venue_id}'
        response = self.make_request(endpoint=endpoint)
        
        if not response:
            logger.warning(f"No details found for venue with id: {venue_id}")
            return {}
        
        venue_details = {
            'name': response.get('name', ''),
            'id': response.get('id', ''),
            'description': response.get('description', ''),
            'address': response.get('address', {}).get('line1', ''),
            'city': response.get('city', {}).get('name', ''),
            'state': response.get('state', {}).get('name', ''),
            'state_code': response.get('state', {}).get('stateCode'),
            'country': response.get('country', {}).get('name'),
            'country_code': response.get('country', {}).get('countryCode'),
            'postalCode': response.get('postalCode', ''),
            'longitude': response.get('location', {}).get('longitude', ''),
            'latitude': response.get('location', {}).get('latitude', ''),
            'timezone': response.get('timezone', ''),
            'currency': response.get('currency', ''),
            'numUpcomingEvents': response.get('upcomingEvents', {}),
            'url': response.get('url', ''),
            'parkingDetail': response.get('parkingDetail', ''),
            'accessibleSeatingDetail': response.get('accessibleSeatingDetail', ''),
            'generalRule': response.get('generalInfo', {}).get('generalRule', ''),
            'childRule': response.get('generalInfo', {}).get('childRule', ''),
        }
        
        return venue_details
    