import requests
import base64
import csv
import time

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
        # Encode the client ID and client secret for Basic Auth
        auth_str = f'{self.client_id}:{self.client_secret}'
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        
        # Set up the token request
        url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {b64_auth_str}'
        }
        data = {
            'grant_type': 'client_credentials'
        }
        
        # Request an access token
        response = requests.post(url, headers=headers, data=data)
        
        # Check for successful response
        if response.status_code == 200:
            token_info = response.json()
            return token_info['access_token']
        else:
            raise Exception(f"Failed to retrieve access token: {response.status_code}, {response.text}")

    # 1. Get all available categories (genres)
    def get_categories(self):
        url = f'{self.base_url}/browse/categories'
        response = requests.get(url, headers=self.headers)
        categories = response.json().get('categories', {}).get('items', [])
        return categories

    # 2a. Get playlists from a specific category (genre)
    def get_playlists_in_category(self, category_id):
        url = f'{self.base_url}/browse/categories/{category_id}/playlists'
        response = requests.get(url, headers=self.headers)
        playlists = response.json().get('playlists', {}).get('items', [])
        return playlists

    # 2b. Get artists from a specific playlist
    def get_artists_from_playlist(self, playlist_id):
        url = f'{self.base_url}/playlists/{playlist_id}'
        response = requests.get(url, headers=self.headers)
        playlist = response.json()

        artists = []
        tracks = playlist.get('tracks', {}).get('items', [])
        for track in tracks:
            try:
                artist = track['track']['artists'][0]
                artist_name = artist['name']
                artist_id = artist['id']

                # Fetch artist details to get popularity
                artist_details_url = f'{self.base_url}/artists/{artist_id}'
                artist_details_response = requests.get(artist_details_url, headers=self.headers)
                print("pog")
                time.sleep(30)

                artist_details_response.raise_for_status()  # Raises an exception for non-2xx status codes
                artist_details = artist_details_response.json()
                print("Delay")
                
                # Add artist data to the list
                artists.append({
                    'name': artist_name,
                    'popularity': artist_details.get('popularity', 'N/A'),
                    'id': artist_id
                })

            except (KeyError, requests.exceptions.RequestException, ValueError) as e:
                print(f"Error processing artist data: {e}")
                continue  # Skip this artist and continue with the next one

        return artists

    # 3. Search for artists in a specific genre
    def search_artists(self, query, limit=10):
        url = f'{self.base_url}/search?q={query}&type=artist&limit={limit}'
        response = requests.get(url, headers=self.headers)
        artists = response.json().get('artists', {}).get('items', [])
        return artists
    
    # 4. Diversify data
    def categorize_popularity(self, popularity):
            """ Categorize artists into low, medium, or high popularity based on a threshold. """
            if popularity < 30:
                return 'low'
            elif 30 <= popularity < 70:
                return 'medium'
            else:
                return 'high'
    
    def balance_artist_popularity(self, artists, target_popularity, genre, category_id, category_name, playlist_id, playlist_name):
        """
        Check if artists' popularity is diverse. Search for more diverse artists if needed.
        
        :param artists: List of artists and their popularity.
        :param target_popularity: Dictionary with the target number of low, medium, and high popularity artists.
        :param genre: Genre for searching more artists if needed.
        :param category_id: ID of the category for metadata.
        :param category_name: Name of the category for metadata.
        :param playlist_id: ID of the playlist for metadata.
        :param playlist_name: Name of the playlist for metadata.
        """
        popularity_groups = {'low': 0, 'medium': 0, 'high': 0}
        
        # Categorize existing artists
        for artist in artists:
            popularity_category = self.categorize_popularity(artist.get('popularity', 0))
            popularity_groups[popularity_category] += 1

        # If the dataset is too skewed in one direction, search for more diverse artists
        for group, count in popularity_groups.items():
            if count < target_popularity[group]:
                needed_artists_count = target_popularity[group] - count
                print(f"Searching for {needed_artists_count} more {group} popularity artists...")
                
                # Adjust search query based on the group (popularity)
                if group == 'low':
                    popularity_query = 'popularity:0-30'
                elif group == 'medium':
                    popularity_query = 'popularity:30-70'
                else:
                    popularity_query = 'popularity:70-100'

                # Search for more artists in the specific genre and popularity range
                additional_artists = self.search_artists(f'{genre} {popularity_query}', limit=needed_artists_count)

                # Add the newly found artists to the artist list with placeholder metadata
                for artist in additional_artists:
                    artists.append({
                        'name': artist['name'],
                        'popularity': artist['popularity'],
                        'category_id': category_id,
                        'category_name': category_name,
                        'playlist_id': playlist_id,
                        'playlist_name': playlist_name
                    })

        return artists
    
    def make_request(self, url):
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', None)
            
            if retry_after:
                print(f"Rate limit exceeded. Wait for {retry_after} seconds before retrying.")
            else:
                print("Rate limit exceeded but no Retry-After header found. Try again later.")
                
        return response

if __name__ == "__main__":
    spotify_manager = SpotifyDataManager('b4593b81912d425d81423fcfc1d50a6a', '1803007734414e2f8f8ad098a592d51f')  # CHANGE THIS LATER, API KEY HERE

    # Create a list to hold all artists before writing to the CSV
    all_artists = []

    #debug in case throttled to see wait time
    spotify_manager.make_request(f'https://api.spotify.com/v1/browse/categories')

    try:
        # 1. Get categories (genres)
        categories = spotify_manager.get_categories()
        for category in categories:
            category_id = category['id']
            category_name = category['name']
            print("On category: " + category_name)
            
            # 2. Get playlists in each category
            playlists = spotify_manager.get_playlists_in_category(category_id)
            for playlist in playlists:
                playlist_id = playlist['id']
                playlist_name = playlist['name']
                print("On playlist: " + playlist_name)

                # 3. Get artists from a specific playlist
                artists = spotify_manager.get_artists_from_playlist(playlist_id)
                time.sleep(1)
                for artist in artists:
                    try:
                        artist_name = artist['name']
                        print("On artist: " + artist_name)
                        artist_popularity = artist.get('popularity', 'N/A')
                    except KeyError as e:
                        print(f"Error processing artist: {e}")
                        continue  # Skip this artist if there's an error

                    # Add artist data to the list
                    all_artists.append({
                        'name': artist_name,
                        'popularity': artist_popularity,
                        'category_id': category_id,
                        'category_name': category_name,
                        'playlist_id': playlist_id,
                        'playlist_name': playlist_name
                    })
        
        # Define a target balance of low, medium, and high popularity artists
        target_popularity = {
            'low': 10, #len(all_artists) // 3,
            'medium': 10, #len(all_artists) // 3,
            'high': 10,#len(all_artists) // 3
        }

        # 4. Check the diversity of artist popularity and balance it if needed
        balanced_artists = spotify_manager.balance_artist_popularity(
            all_artists, target_popularity, 'genre'
        )

        # Open a CSV file to write results to
        with open('spotify_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write headers for the CSV file
            writer.writerow(['Category ID', 'Category Name', 'Playlist ID', 'Playlist Name', 'Artist Name', 'Artist Popularity'])

            # Write the balanced artist data to the CSV file
            for artist in balanced_artists:
                writer.writerow([
                    artist.get('category_id'),
                    artist.get('category_name'),
                    artist.get('playlist_id'),
                    artist.get('playlist_name'),
                    artist.get('name'),
                    artist.get('popularity')
                ])

        print("Data has been successfully saved to 'spotify_data.csv'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")