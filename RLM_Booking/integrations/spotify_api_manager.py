import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any

# Import other modules it inherits
from api_manager import APIManager   

# Load environment variables
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Configure logging for class debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyAPIManager(APIManager):
    SPOTIFY_BASE_URL = 'https://api.spotify.com/v1'

    def __init__(self):
        """
        Initializes the SpotifyAPIManager with the necessary credentials and base URL.
        """
        credentials = {
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }
        super().__init__(
            base_url=self.SPOTIFY_BASE_URL,
            auth_type='Bearer',
            credentials=credentials
        )

    def fetch_data_in_arg_order(self, endpoint: str, key: str) -> List[Dict[str, Any]]:
        """
        Generic method to fetch data from a given endpoint.
        
        Args:
            endpoint (str): The API endpoint to fetch data from.
            key (str): The key to extract data from the response. Think of this as the data field requested.
        
        Returns:
            A list of dictionaries containing the requested data, or an empty list if the request fails.
        """
        logging.debug(f"Fetching data from endpoint {endpoint}")
        response = self.make_request(endpoint)
        data = response.get(key, {}).get('items', [])
        
        if not data:
            logging.warning(f"No data found at endpoint {endpoint}")
        
        return data

    def fetch_categories(self) -> List[Dict[str, Any]]:
        """
        Fetches Spotify categories (genres) from the API.
        
        Returns:
            A list of category dictionaries, or an empty list if the request fails.
        """
        logging.debug("Fetching categories from Spotify API")
        response = self.make_request("browse/categories")
        categories = response.get('categories', {}).get('items', [])
        
        if not categories:
            logging.warning("No categories found in the API response")
        
        return categories

    def fetch_playlists_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """
        Fetches playlists for a given Spotify category.
        
        Args:
            category_id (str): The Spotify ID of the category.
        
        Returns:
            A list of playlist dictionaries, or an empty list if the request fails.
        """
        logging.debug(f"Fetching playlists for category {category_id}")
        endpoint = f"browse/categories/{category_id}/playlists"
        response = self.make_request(endpoint)
        playlists = response.get('playlists', {}).get('items', [])
        
        if not playlists:
            logging.warning(f"No playlists found for category {category_id}")
        
        return playlists

    def fetch_artists_in_playlist(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Fetches artists from a given Spotify playlist by first retrieving tracks,
        and then gathering artist details for each track.
        
        Args:
            playlist_id (str): The Spotify ID of the playlist.
        
        Returns:
            A list of artist dictionaries, or an empty list if the request fails.
        """
        logging.debug(f"Fetching artists for playlist {playlist_id}")
        endpoint = f"playlists/{playlist_id}/tracks"
        response = self.make_request(endpoint)
        tracks = response.get('items', [])
        
        if not tracks:
            logging.warning(f"No tracks found for playlist {playlist_id}.")
            return []
        
        artists = []
        for track in tracks:
            artist = track.get('track', {}).get('artists', [{}])[0]
            artist_id = artist.get('id')
            if artist_id:
                artist_details = self.fetch_artist_details(artist_id)
                if artist_details:
                    artists.append(artist_details)
        
        return artists

    def fetch_artist_details(self, artist_id: str) -> Dict[str, Any]:
        """
        Fetches detailed information for a given artist by their Spotify ID.
        
        Args:
            artist_id (str): The Spotify ID of the artist.
        
        Returns:
            A dictionary with artist details, or an empty dictionary if the request fails.
        """
        logging.debug(f"Fetching details for artist {artist_id}")
        endpoint = f"artists/{artist_id}"
        artist_data = self.make_request(endpoint)
        
        if not artist_data:
            logging.warning(f"No artist data found for {artist_id}.")
            return {}
        
        artist_details = {
            'artist_name': artist_data.get('name', 'Unknown Artist'),
            'genre': ', '.join(artist_data.get('genres', [])),
            'popularity': artist_data.get('popularity', 0),
            'followers': artist_data.get('followers', {}).get('total', 0),
            'external_url': artist_data.get('external_urls', {}).get('spotify', '')
        }
        
        return artist_details
