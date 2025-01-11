import logging
from typing import List, Dict, Any

from integrations.spotify_api_manager import SpotifyAPIManager
from utils.data_writer import DataWriter
from utils.progress_manager import ProgressManager

class APIDataStorageService:
    def __init__(self, data_writer: DataWriter, progress_manager: ProgressManager):
        """
        Constructor for APIDataStorageService.

        Args:
            data_writer (DataWriter): An instance of DataWriter, a module to store fetched data.
            progress_manager (ProgressManager): An instance of ProgressManager, a module to start from the most recent fetched data.
        """
        self.data_writer = data_writer
        self.progress_manager = progress_manager
    
    def fetch_and_save_spotify_data(self, spotify_api_manager: SpotifyAPIManager, data_point_limit: int = 10000) -> None:
        """
        Fetches data from the Spotify API and saves it to a CSV file.

        Args:
            spotify_api_manager (SpotifyAPIManager): An instance of SpotifyAPIManager to manage Spotify APi calls.
            data_point_limit (int): The maximum number of data points to fetch and save.
        """
        logging.debug("Starting fetch_and_save_spotify_data")
        data_points_collected = len(self.data_writer.existing_entries)

        categories = spotify_api_manager.fetch_categories()
        for category in categories:
            if self.progress_manager.should_skip(category['id'], 'category'):
                continue

            playlists = spotify_api_manager.fetch_playlists(category['id'])
            for playlist in playlists:
                if self.progress_manager.should_skip(playlist['id'], 'playlist'):
                    continue

                artists = spotify_api_manager.fetch_artists(playlist['id'])
                for artist in artists:
                    if self.progress_manager.should_skip(artist['artist_name'], 'track'):
                        continue

                    if self.data_writer.write_entry_to_csv(artist):
                        data_points_collected += 1
                        logging.info(f"Artist {artist['artist_name']} written to CSV.")
                        
                        self.progress_manager.save_progress(
                            last_category_id=category['id'],
                            last_playlist_id=playlist['id'],
                            last_track_id=artist['artist_name']
                        )

                    if data_points_collected >= data_point_limit:
                        logging.info("Data point limit reached.")
                        return
                    
    def fetch_and_save_ticketmaster_data(self, ticketmaster_api_manager: TicketmasterAPIManager, artist_name: str, csv_file: str) -> None:
        """Fetches data from the Ticketmaster API and saves it to a CSV file."""
        logging.debug("Starting fetch_and_save_ticketmaster_data")
        data = ticketmaster_api_manager.get_ticketmaster_data(artist_name)
        
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['event_name', 'date', 'venue', 'city', 'state', 'country', 'price'])
            for event in data.get('_embedded', {}).get('events', []):
                event_name = event.get('name')
                date = event.get('dates', {}).get('start', {}).get('localDate')
                venue = event.get('_embedded', {}).get('venues', [{}])[0].get('name')
                city = event.get('_embedded', {}).get('venues', [{}])[0].get('city', {}).get('name')
                state = event.get('_embedded', {}).get('venues', [{}])[0].get('state', {}).get('stateCode')
                country = event.get('_embedded', {}).get('venues', [{}])[0].get('country', {}).get('countryCode')
                price = event.get('priceRanges', [{}])[0].get('min')
                writer.writerow([event_name, date, venue, city, state, country, price])
                    
# background task scheduler to avoid rate limits and update ML data
# Ask Copilot about using Celery to run this service
    # Celery runs this in the background every period you set (ex. 1 hour)