import os
import base64
import requests
import csv
import logging
import time
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

# Configure logging for your script
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress requests and urllib3 internal logging below WARNING level
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

class SpotifyDataManager:
    def __init__(self, client_id: str, client_secret: str):
        logging.debug("Initializing SpotifyDataManager")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'https://api.spotify.com/v1'
        
        try:
            # Attempt to get the access token
            self.access_token = self.get_access_token()
            self.headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            logging.debug("SpotifyDataManager initialized successfully")
        
        except Exception as e:
            # Handle initialization failure due to token retrieval issues
            logging.error(f"Failed to initialize SpotifyDataManager: {e}")
            self.access_token = None
            self.headers = {}

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
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if not access_token:
                raise KeyError("Access token not found in the response")

            logging.debug("Access token retrieved successfully")
            return access_token

        except (requests.RequestException, KeyError) as e:
            logging.error(f"Failed to retrieve access token: {e}")
            raise Exception(f"Access token retrieval failed: {e}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    def refresh_access_token(self):
        """
        Refreshes the access token when it has expired or is invalid.
        """
        logging.info("Refreshing access token")
        self.access_token = self.get_access_token()  # Get a new access token
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def make_request(self, url: str) -> Dict[str, Any]:
        """
        Helper method to make API requests to Spotify, handle token expiration,
        rate limits, and catch common exceptions.
        
        Args:
            url (str): The URL for the Spotify API request.
        
        Returns:
            dict: The JSON response from the API if successful, otherwise an empty dictionary.
        """
        try:
            response = requests.get(url, headers=self.headers)
            
            # If the token has expired, refresh the token and retry the request
            if response.status_code == 401:
                logging.info("Token expired or invalid, refreshing access token...")
                self.refresh_access_token()
                response = requests.get(url, headers=self.headers)  # Retry with new token
            
            # If rate-limited, handle 429 Too Many Requests response
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))  # Get retry delay from headers
                logging.warning(f"Rate limit hit. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self.make_request(url)  # Retry request after waiting
            
            response.raise_for_status()  # Raise for bad HTTP responses
            
            return response.json()  # Return the JSON response
        
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return {}
        
        except ValueError:
            logging.error("Failed to decode JSON response.")
            return {}
        
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return {}

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Fetches Spotify categories (genres) from the API.
        
        Returns:
            A list of category dictionaries, or an empty list if the request fails or no categories are found.
        """
        logging.debug("Fetching categories from Spotify API")
        url = f'{self.base_url}/browse/categories'
        
        # Use the centralized request method to handle the API call
        json_response = self.make_request(url)
        
        # Extract categories from the response
        categories = json_response.get('categories', {}).get('items', [])
        
        if not categories:
            logging.warning("No categories found in the API response")
        
        logging.debug(f"Categories retrieved: {categories}")
        return categories

    def get_playlists_in_category(self, category_id: str) -> List[Dict[str, Any]]:
        """
        Fetches playlists for a given Spotify category.
        
        Args:
            category_id (str): The Spotify ID of the category.
        
        Returns:
            A list of playlist dictionaries, or an empty list if the request fails or no playlists are found.
        """
        logging.debug(f"Fetching playlists for category {category_id}")
        url = f'{self.base_url}/browse/categories/{category_id}/playlists'
        
        # Make the request using the centralized helper
        json_response = self.make_request(url)
        
        playlists = json_response.get('playlists', {}).get('items', [])
        
        if not playlists:
            logging.warning(f"No playlists found for category {category_id}")
        
        return playlists

    def get_tracks_from_playlist(self, playlist_id: str) -> List[str]:
        """
        Fetches tracks from a given Spotify playlist and extracts the unique artist IDs.
        
        Args:
            playlist_id (str): The Spotify ID of the playlist.
        
        Returns:
            A list of unique artist IDs from the playlist.
        """
        logging.debug(f"Fetching tracks for playlist {playlist_id}")
        url = f'{self.base_url}/playlists/{playlist_id}/tracks'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Extract artist IDs from the track list
            tracks = response.json().get('items', [])
            artist_ids = []
            
            if not tracks:
                logging.warning(f"No tracks found for playlist {playlist_id}.")
                return []
            
            for track in tracks:
                # Each track can have multiple artists; get all artist IDs
                artists = track.get('track', {}).get('artists', [])
                for artist in artists:
                    artist_id = artist.get('id')
                    if artist_id and artist_id not in artist_ids:
                        artist_ids.append(artist_id)
            
            logging.debug(f"Artist IDs extracted from playlist {playlist_id}: {artist_ids}")
            return artist_ids
        
        except requests.RequestException as e:
            logging.error(f"Error fetching tracks from playlist {playlist_id}: {e}")
            return []
        
    def get_artist_details(self, artist_id: str) -> Dict[str, Any]:
        """
        Fetches detailed information for a given artist by their Spotify ID.
        
        Args:
            artist_id (str): The Spotify ID of the artist.
        
        Returns:
            A dictionary with artist details (for CSV), or an empty dictionary if the request fails.
        """
        logging.debug(f"Fetching details for artist {artist_id}")
        artist_details_url = f'{self.base_url}/artists/{artist_id}'
        
        # Use the centralized request method to handle the API call
        artist_data = self.make_request(artist_details_url)
        
        if not artist_data:
            logging.warning(f"No artist data found for {artist_id}.")
            return {}
        
        # Parse artist details
        artist_details = {
            'artist_name': artist_data.get('name', 'Unknown Artist'),
            'genre': ', '.join(artist_data.get('genres', [])),
            'popularity': artist_data.get('popularity', 0),
            'followers': artist_data.get('followers', {}).get('total', 0),
            'external_url': artist_data.get('external_urls', {}).get('spotify', '')
        }
        
        logging.debug(f"Artist details retrieved for {artist_id}: {artist_details}")
        return artist_details

        
    def get_playlist_artists(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Fetches artists from a given Spotify playlist by first retrieving tracks,
        and then gathering artist details for each track.
        
        Args:
            playlist_id (str): The Spotify ID of the playlist.
        
        Returns:
            A list of artist dictionaries, or an empty list if the request fails or no artists are found.
        """
        logging.debug(f"Fetching artists for playlist {playlist_id}")
        url = f'{self.base_url}/playlists/{playlist_id}/tracks'
        
        # Make the request using the centralized helper
        json_response = self.make_request(url)
        
        tracks = json_response.get('items', [])
        
        if not tracks:
            logging.warning(f"No tracks found for playlist {playlist_id}.")
            return []
        
        artists = []
        for track in tracks:
            artist = track.get('track', {}).get('artists', [{}])[0]
            artist_id = artist.get('id')
            if artist_id:
                artist_details = self.get_artist_details(artist_id)
                if artist_details:
                    artists.append(artist_details)
        
        return artists


    def read_existing_entries(self, filename: str) -> set:
        """
        Read existing entries from the CSV file to avoid duplicates.
        
        Args:
            filename (str): Name of the CSV file.
        
        Returns:
            set: Set of existing entries, where each entry is a tuple of (artist_name, genre, popularity, followers, external_url).
        """
        logging.debug(f"Reading existing entries from {filename}")
        existing_entries = set()
        
        try:
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                # Check if all expected columns are present in the CSV
                expected_columns = {'artist_name', 'genre', 'popularity', 'followers', 'external_url'}
                
                if not expected_columns.issubset(reader.fieldnames):
                    logging.error(f"Missing columns in the CSV file. Expected columns: {expected_columns}")
                    return existing_entries
                
                # Read and store existing entries
                for row in reader:
                    try:
                        # Normalize the data by stripping whitespace and converting to strings
                        entry = (
                            row['artist_name'].strip(),
                            row['genre'].strip(),
                            str(row['popularity']).strip(),  # Ensure consistency in types
                            str(row['followers']).strip(),   # Convert followers to string
                            row['external_url'].strip()      # Strip URL whitespace
                        )
                        existing_entries.add(entry)
                    except KeyError as e:
                        logging.warning(f"Missing expected field {e} in a row. Skipping row: {row}")
                    except Exception as e:
                        logging.error(f"Error processing row: {e}. Skipping row: {row}")
                
                logging.debug(f"Successfully read {len(existing_entries)} existing entries from {filename}")
        
        except FileNotFoundError:
            logging.info(f"File {filename} not found. A new file will be created.")
        
        except Exception as e:
            logging.error(f"Error reading existing entries from CSV: {e}")
        
        return existing_entries

    def load_progress(self, progress_file: str) -> dict:
        """
        Load the last progress from the progress file if it exists.
        
        Args:
            progress_file (str): Path to the progress file.
        
        Returns:
            dict: A dictionary containing the last processed category, playlist, and track.
        """
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as file:
                return json.load(file)
        else:
            # Return a default structure if no progress file exists
            return {"last_category_id": None, "last_playlist_id": None, "last_track_id": None}

    def save_progress(self, progress_file: str, category_id: str, playlist_id: str, track_id: str) -> None:
        """
        Save the current progress to a file.
        
        Args:
            progress_file (str): Path to the progress file.
            category_id (str): The last processed category ID.
            playlist_id (str): The last processed playlist ID.
            track_id (str): The last processed track ID.
        """
        progress = {
            "last_category_id": category_id,
            "last_playlist_id": playlist_id,
            "last_track_id": track_id
        }
        with open(progress_file, 'w') as file:
            json.dump(progress, file)

    def fetch_and_save_spotify_data(self, output_file='spotify_data.csv', data_point_limit=10000, progress_file='progress.json'):
        """
        Fetches data from Spotify, checks for duplicates, and saves artist data to a CSV incrementally.
        Resumes from the last processed category, playlist, and track if the script is restarted.
        
        Args:
            output_file (str): Name of the output CSV file.
            data_point_limit (int): The maximum number of data points to collect.
            progress_file (str): Name of the progress file to track the last processed items.
        """
        logging.debug("Starting fetch_and_save_spotify_data")
        
        # Load the last progress (if any)
        progress = self.load_progress(progress_file)
        last_category_id = progress.get('last_category_id')
        last_playlist_id = progress.get('last_playlist_id')
        last_track_id = progress.get('last_track_id')
        
        try:
            # Fetch all categories
            categories = self.get_categories()
            
            # Define the CSV headers
            headers = ['artist_name', 'genre', 'popularity', 'followers', 'external_url']
            
            # Read existing entries to avoid duplicates
            existing_entries = self.read_existing_entries(output_file)
            
            # Open CSV file in append mode
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                
                # Write headers if the file is empty
                if file.tell() == 0:
                    writer.writeheader()
                
                data_points_collected = len(existing_entries)
                
                # Loop through categories
                category_found = False
                for category in categories:
                    try:
                        category_id = category.get('id')
                        category_name = category.get('name')
                        
                        if not category_id or not category_name:
                            logging.warning("Category ID or name is missing, skipping.")
                            continue
                        
                        # Skip categories that have already been processed
                        if last_category_id and category_id != last_category_id and not category_found:
                            continue
                        category_found = True
                        
                        # Fetch playlists in the category
                        playlists = self.get_playlists_in_category(category_id)
                        
                        playlist_found = False
                        for playlist in playlists:
                            try:
                                playlist_id = playlist.get('id')
                                playlist_name = playlist.get('name')
                                
                                if not playlist_id or not playlist_name:
                                    logging.warning(f"Playlist ID or name is missing for playlist in category {category_name}, skipping.")
                                    continue
                                
                                # Skip playlists that have already been processed
                                if last_playlist_id and playlist_id != last_playlist_id and not playlist_found:
                                    continue
                                playlist_found = True
                                
                                # Fetch artists from the playlist
                                artist_found = False
                                artists = self.get_playlist_artists(playlist_id)
                                
                                for artist in artists:
                                    try:
                                        artist_name = artist.get('artist_name', 'Unknown Artist')
                                        if last_track_id and artist_name != last_track_id and not artist_found:
                                            # Skip until we reach the last processed track
                                            continue
                                        artist_found = True
                                        
                                        if not artist:
                                            logging.warning(f"Encountered None artist in playlist {playlist_name}, skipping.")
                                            continue
                                        
                                        artist_data = {
                                            'artist_name': artist_name,
                                            'genre': artist.get('genre', ''),
                                            'popularity': artist.get('popularity', 0),
                                            'followers': artist.get('followers', 0),
                                            'external_url': artist.get('external_url', '')
                                        }
                                        
                                        # Create a tuple to represent the artist entry
                                        entry = (artist_data['artist_name'], artist_data['genre'], artist_data['popularity'], artist_data['followers'], artist_data['external_url'])
                                        
                                        # Check for duplicates and write the artist to the CSV if it's new
                                        if entry not in existing_entries:
                                            writer.writerow(artist_data)
                                            existing_entries.add(entry)
                                            data_points_collected += 1
                                            logging.info(f"Artist {artist_data['artist_name']} written to CSV.")
                                            
                                            # Save progress after writing the artist
                                            self.save_progress(progress_file, category_id, playlist_id, artist_name)
                                            
                                            # Add delay to avoid hitting rate limit
                                            logging.debug("Applying delay to avoid (burst) rate limit")
                                            time.sleep(0.3)  # 300 milliseconds delay (adjust as needed)
                                            
                                            # Stop collecting if the data point limit is reached
                                            if data_points_collected >= data_point_limit:
                                                logging.info(f"Data point limit of {data_point_limit} reached. Stopping data collection.")
                                                return
                                        else:
                                            logging.info(f"Duplicate entry for artist {artist_data['artist_name']} skipped.")
                                    except Exception as e:
                                        logging.error(f"Error processing artist in playlist {playlist_name}: {e}")
                                        continue  # Continue to the next artist
                                
                                # Save progress at the end of the playlist
                                self.save_progress(progress_file, category_id, playlist_id, None)
                            
                            except Exception as e:
                                logging.error(f"Error processing playlist {playlist_name} in category {category_name}: {e}")
                                continue  # Continue to the next playlist
                    
                    except Exception as e:
                        logging.error(f"Error processing category {category_name}: {e}")
                        continue  # Continue to the next category
        
        except Exception as e:
            logging.error(f"An error occurred during data collection: {e}")

# Package everything and run script directly (for testing)
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