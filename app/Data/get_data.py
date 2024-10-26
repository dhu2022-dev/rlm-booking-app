import requests
import base64
import csv
import os
import logging
from dotenv import load_dotenv

class SpotifyDataManager:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = 'https://api.spotify.com/v1'
        self.access_token = self.get_access_token()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_access_token(self):
        """
        Retrieves access token for Spotify API
        """
        auth_str = f'{self.client_id}:{self.client_secret}'
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        
        url = 'https://accounts.spotify.com/api/token'
        headers = {'Authorization': f'Basic {b64_auth_str}'}
        data = {'grant_type': 'client_credentials'}

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Failed to retrieve access token: {response.status_code}, {response.text}")

    def api_get_request(self, endpoint):
        """
        Handles GET requests to Spotify API
        """
        url = f'{self.base_url}/{endpoint}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to make API call: {response.status_code}, {response.text}")

    def get_categories(self):
        """
        Get all available categories (genres)
        """
        return self.api_get_request('browse/categories').get('categories', {}).get('items', [])

    def get_playlists_in_category(self, category_id):
        """
        Get playlists from a specific category (genre)
        """
        return self.api_get_request(f'browse/categories/{category_id}/playlists').get('playlists', {}).get('items', [])

    def get_playlist_artists(self, playlist_id):
        """
        Get artists from a specific playlist
        """
        tracks = self.api_get_request(f'playlists/{playlist_id}/tracks').get('items', [])
        artists = []
        for track in tracks:
            artist_info = track.get('track', {}).get('artists', [])
            for artist in artist_info:
                artists.append(artist)
        return artists

    def search_artist(self, artist_id):
        """
        Get detailed information for an artist by their Spotify ID
        """
        return self.api_get_request(f'artists/{artist_id}')

    def categorize_popularity(self, popularity):
        """
        Categorizes the popularity of an artist as 'low', 'medium', or 'high'
        """
        if popularity < 30:
            return 'low'
        elif popularity < 70:
            return 'medium'
        else:
            return 'high'

    def balance_artist_popularity(self, artists, target_popularity):
        """
        Ensures a balanced mix of artists by popularity category (low, medium, high)
        """
        balanced_artists = []
        popularity_count = {'low': 0, 'medium': 0, 'high': 0}

        for artist in artists:
            category = self.categorize_popularity(artist['popularity'])
            if popularity_count[category] < target_popularity[category]:
                balanced_artists.append(artist)
                popularity_count[category] += 1

        return balanced_artists
    
    def read_existing_entries(self, filename: str) -> set:
        existing_entries = set()
        try:
            with open(filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    entry = (row['Category ID'], row['Category Name'], row['Playlist ID'], row['Playlist Name'], row['Artist Name'], row['Artist Popularity'])
                    existing_entries.add(entry)
        except FileNotFoundError:
            logging.info(f"File {filename} not found. A new file will be created.")
        except Exception as e:
            logging.error(f"Error reading existing entries from CSV: {e}")
        return existing_entries

    def write_to_csv(self, filename, data, headers):
        """
        Write the provided data to a CSV file
        """
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(data)
            print(f"Data has been successfully saved to '{filename}'.")
        except Exception as e:
            print(f"Error writing to CSV: {e}")

    def fetch_and_save_spotify_data(self, categories_limit=10, playlists_limit=5, output_file='spotify_data.csv'):
        """
        Fetches data from Spotify, balances the artist popularity, and saves it to a CSV incrementally, skipping duplicates.
        """
        try:
            categories = self.get_categories()[:categories_limit]
            headers = ['Category ID', 'Category Name', 'Playlist ID', 'Playlist Name', 'Artist Name', 'Artist Popularity']
            existing_entries = self.read_existing_entries(output_file)

            # Open the CSV file in append mode
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                
                # Write headers only if the file is empty
                if file.tell() == 0:
                    writer.writeheader()

                # Go through categories
                for category in categories:
                    category_id = category['id']
                    category_name = category['name']
                    playlists = self.get_playlists_in_category(category_id)[:playlists_limit]
                    
                    # Go through playlists
                    for playlist in playlists:
                        playlist_id = playlist['id']
                        playlist_name = playlist['name']
                        artists = self.get_playlist_artists(playlist_id)

                        # Go through artists
                        for artist in artists:
                            artist_name = artist.get('name', 'Unknown Artist')
                            artist_popularity = artist.get('popularity', 0)

                            artist_data = {
                                'Category ID': category_id,
                                'Category Name': category_name,
                                'Playlist ID': playlist_id,
                                'Playlist Name': playlist_name,
                                'Artist Name': artist_name,
                                'Artist Popularity': artist_popularity
                            }

                            # Create the entry
                            entry = (category_id, category_name, playlist_id, playlist_name, artist_name, artist_popularity)
                            
                            # Check for duplicates, write to output if it's new
                            if entry not in existing_entries:
                                writer.writerow(artist_data)
                                existing_entries.add(entry)
                                logging.info(f"Artist {artist_name} written to CSV.")
                            else:
                                logging.info(f"Duplicate entry for artist {artist_name} skipped.")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

    # Package everything and run script directly (for testing)
    def main():
        # get credentials from .env file
        load_dotenv()
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        
        # Initialize the SpotifyDataManager
        spotify_manager = SpotifyDataManager(client_id=client_id, client_secret=client_secret)
        
        # Fetch and save data to a CSV file
        spotify_manager.fetch_and_save_spotify_data()

    if __name__ == "__main__":
        main()