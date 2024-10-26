import os
import base64
import requests
import csv
import logging
import time
from dotenv import load_dotenv
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotifyDataManager:
    def __init__(self, client_id: str, client_secret: str):
        logging.debug("Initializing SpotifyDataManager")
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'https://api.spotify.com/v1'
        self.access_token = self.get_access_token()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_access_token(self) -> str:
        """
        Retrieves access token for Spotify API
        """
        logging.debug("Getting access token")
        auth_str = f'{self.client_id}:{self.client_secret}'
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        
        url = 'https://accounts.spotify.com/api/token'
        headers = {'Authorization': f'Basic {b64_auth_str}'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            logging.debug("Access token retrieved successfully")
            return response.json()['access_token']
        else:
            logging.error(f"Failed to retrieve access token: {response.status_code}, {response.text}")
            raise Exception(f"Failed to retrieve access token: {response.status_code}, {response.text}")

    def get_categories(self) -> List[Dict[str, Any]]:
        logging.debug("Getting categories")
        url = f'{self.base_url}/browse/categories'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            categories = response.json().get('categories', {}).get('items', [])
            if categories is None:
                logging.error("No categories found in the response.")
                return []
            logging.debug(f"Categories retrieved: {categories}")
            return categories
        except requests.RequestException as e:
            logging.error(f"Error fetching categories: {e}")
            return []

    def get_playlists_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        logging.debug(f"Getting playlists for category {category_id}")
        url = f'{self.base_url}/browse/categories/{category_id}/playlists'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            playlists = response.json().get('playlists', {}).get('items', [])
            if playlists is None:
                logging.error(f"No playlists found for category {category_id}.")
                return []
            logging.debug(f"Playlists retrieved for category {category_id}: {playlists}")
            return playlists
        except requests.RequestException as e:
            logging.error(f"Error fetching playlists in category {category_id}: {e}")
            return []

    def get_playlist_artists(self, playlist_id: str) -> List[Dict[str, Any]]:
        logging.debug(f"Getting artists for playlist {playlist_id}")
        url = f'{self.base_url}/playlists/{playlist_id}/tracks'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tracks = response.json().get('items', [])
            if tracks is None:
                logging.error(f"No tracks found for playlist {playlist_id}.")
                return []
            artists = []
            for track in tracks:
                artist = track['track']['artists'][0]
                artist_id = artist['id']
                artist_details_url = f'{self.base_url}/artists/{artist_id}'
                try:
                    artist_response = requests.get(artist_details_url, headers=self.headers)
                    artist_response.raise_for_status()
                    artist_data = artist_response.json()
                    artist_details = {
                        'artist_name': artist_data.get('name', 'Unknown Artist'),
                        'genre': ', '.join(artist_data.get('genres', [])),
                        'popularity': artist_data.get('popularity', 0),
                        'followers': artist_data.get('followers', {}).get('total', 0),
                        'external_url': artist_data.get('external_urls', {}).get('spotify', '')
                    }
                    artists.append(artist_details)
                    # Add a delay to avoid hitting rate limits
                    time.sleep(1)  # Adjust the delay as needed
                except requests.RequestException as e:
                    logging.error(f"Error fetching artist details for {artist_id}: {e}")
            logging.debug(f"Artists retrieved for playlist {playlist_id}: {artists}")
            return artists
        except requests.RequestException as e:
            logging.error(f"Error fetching artists from playlist {playlist_id}: {e}")
            return []

    def fetch_and_save_spotify_data(self, categories_limit=10, playlists_limit=5, output_file='spotify_data.csv'):
        """
        Fetches data from Spotify, balances the artist popularity, and saves it to a CSV incrementally, skipping duplicates.
        """
        logging.debug("Starting fetch_and_save_spotify_data")
        try:
            categories = self.get_categories()[:categories_limit]
            headers = ['artist_name', 'genre', 'popularity', 'followers', 'external_url']
            existing_entries = self.read_existing_entries(output_file)

            # Open the CSV file in append mode
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                
                # Write headers only if the file is empty
                if file.tell() == 0:
                    writer.writeheader()

                for category in categories:
                    if category is None:
                        logging.warning("Encountered None category, skipping.")
                        continue

                    category_id = category.get('id')
                    category_name = category.get('name')
                    if not category_id or not category_name:
                        logging.warning("Category ID or name is missing, skipping.")
                        continue

                    playlists = self.get_playlists_in_category(category_id)[:playlists_limit]
                    for playlist in playlists:
                        if playlist is None:
                            logging.warning("Encountered None playlist, skipping.")
                            continue

                        playlist_id = playlist.get('id')
                        playlist_name = playlist.get('name')
                        if not playlist_id or not playlist_name:
                            logging.warning("Playlist ID or name is missing, skipping.")
                            continue

                        artists = self.get_playlist_artists(playlist_id)
                        for artist in artists:
                            if artist is None:
                                logging.warning("Encountered None artist, skipping.")
                                continue

                            artist_data = {
                                'artist_name': artist.get('artist_name', 'Unknown Artist'),
                                'genre': artist.get('genre', ''),
                                'popularity': artist.get('popularity', 0),
                                'followers': artist.get('followers', 0),
                                'external_url': artist.get('external_url', '')
                            }

                            entry = (artist_data['artist_name'], artist_data['genre'], artist_data['popularity'], artist_data['followers'], artist_data['external_url'])
                            if entry not in existing_entries:
                                writer.writerow(artist_data)
                                existing_entries.add(entry)
                                logging.info(f"Artist {artist_data['artist_name']} written to CSV.")
                            else:
                                logging.info(f"Duplicate entry for artist {artist_data['artist_name']} skipped.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def read_existing_entries(self, filename: str) -> set:
        """
        Read existing entries from the CSV file to avoid duplicates.
        
        Args:
            filename (str): Name of the CSV file.
        
        Returns:
            set: Set of existing entries.
        """
        logging.debug(f"Reading existing entries from {filename}")
        existing_entries = set()
        try:
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    entry = (row['artist_name'], row['genre'], row['popularity'], row['followers'], row['external_url'])
                    existing_entries.add(entry)
            logging.debug(f"Existing entries read: {existing_entries}")
        except FileNotFoundError:
            logging.info(f"File {filename} not found. A new file will be created.")
        except Exception as e:
            logging.error(f"Error reading existing entries from CSV: {e}")
        return existing_entries

# Package everything and run script directly (for testing)
# It WILL run forever until you collect everything you need
def main():
    # get credentials from .env file
    load_dotenv()
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    logging.debug(f"Client ID: {client_id}")
    logging.debug(f"Client Secret: {client_secret}")

    # Initialize the SpotifyDataManager
    spotify_manager = SpotifyDataManager(client_id=client_id, client_secret=client_secret)
    
    # Fetch and save data to a CSV file
    spotify_manager.fetch_and_save_spotify_data()

if __name__ == "__main__":
    main()