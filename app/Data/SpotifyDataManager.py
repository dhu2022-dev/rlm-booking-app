import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

import APIManager  # Assuming APIManager is in a separate file
import ProgressManager  # Import the refactored ProgressManager
import DataWriter  # Import the refactored DataWriter

# Configure logging for script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyDataManager:
    def __init__(self, api_manager: APIManager):
        """
        Initializes the SpotifyDataManager with an APIManager instance.
        
        Args:
            api_manager (APIManager): An instance of APIManager configured for Spotify API.
        """
        self.api_manager = api_manager

    def fetch_categories(self) -> List[Dict[str, Any]]:
        """
        Fetches Spotify categories (genres) from the API.
        
        Returns:
            A list of category dictionaries, or an empty list if the request fails.
        """
        logging.debug("Fetching categories from Spotify API")
        response = self.api_manager.make_request("browse/categories")
        categories = response.get('categories', {}).get('items', [])
        
        if not categories:
            logging.warning("No categories found in the API response")
        
        return categories

    def fetch_playlists(self, category_id: str) -> List[Dict[str, Any]]:
        """
        Fetches playlists for a given Spotify category.
        
        Args:
            category_id (str): The Spotify ID of the category.
        
        Returns:
            A list of playlist dictionaries, or an empty list if the request fails.
        """
        logging.debug(f"Fetching playlists for category {category_id}")
        endpoint = f"browse/categories/{category_id}/playlists"
        response = self.api_manager.make_request(endpoint)
        playlists = response.get('playlists', {}).get('items', [])
        
        if not playlists:
            logging.warning(f"No playlists found for category {category_id}")
        
        return playlists

    def fetch_artists(self, playlist_id: str) -> List[Dict[str, Any]]:
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
        response = self.api_manager.make_request(endpoint)
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
        artist_data = self.api_manager.make_request(endpoint)
        
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

    def fetch_and_save_spotify_data(self, data_writer: DataWriter, progress_manager: ProgressManager, data_point_limit=10000):
        logging.debug("Starting fetch_and_save_spotify_data")
        data_points_collected = len(data_writer.existing_entries)

        # Loop through categories, playlists, and artists, using DataWriter and ProgressManager
        for category in self.fetch_categories():
            if progress_manager.should_skip(category['id'], 'category'):
                continue

            for playlist in self.fetch_playlists(category['id']):
                if progress_manager.should_skip(playlist['id'], 'playlist'):
                    continue

                for artist in self.fetch_artists(playlist['id']):
                    if progress_manager.should_skip(artist['artist_name'], 'track'):
                        continue

                    # Write artist data to CSV if not a duplicate and within the limit
                    if data_writer.write_entry_to_csv(artist):
                        data_points_collected += 1
                        logging.info(f"Artist {artist['artist_name']} written to CSV.")
                        
                        # Save progress
                        progress_manager.save_progress(
                            last_category_id=category['id'],
                            last_playlist_id=playlist['id'],
                            last_track_id=artist['artist_name']
                        )

                    if data_points_collected >= data_point_limit:
                        logging.info("Data point limit reached.")
                        return

# Main function to initialize components and run the process
def main():
    # Load credentials from environment variables
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    # Initialize APIManager for Spotify with OAuth2 credentials
    api_manager = APIManager(
        base_url="https://api.spotify.com/v1",
        auth_type="Bearer",
        credentials={'client_id': client_id, 'client_secret': client_secret}
    )

    # Initialize SpotifyDataManager, ProgressManager, and DataWriter
    spotify_manager = SpotifyDataManager(api_manager)
    data_writer = DataWriter('spotify_data.csv', headers=['artist_name', 'genre', 'popularity', 'followers', 'external_url'])
    progress_manager = ProgressManager('progress.json')

    # Fetch and save data
    spotify_manager.fetch_and_save_spotify_data(data_writer, progress_manager, data_point_limit=10000)

if __name__ == "__main__":
    main()
