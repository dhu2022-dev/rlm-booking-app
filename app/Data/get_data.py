import requests
import base64
import csv

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
        Fetches data from Spotify, balances the artist popularity, and saves it to a CSV
        """
        try:
            categories = self.get_categories()[:categories_limit]
            all_artists = []
            for category in categories:
                category_id = category['id']
                category_name = category['name']
                playlists = self.get_playlists_in_category(category_id)[:playlists_limit]

                for playlist in playlists:
                    playlist_id = playlist['id']
                    playlist_name = playlist['name']
                    artists = self.get_playlist_artists(playlist_id)

                    for artist in artists:
                        artist_name = artist.get('name', 'Unknown Artist')
                        artist_popularity = artist.get('popularity', 0)

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
                'low': 10,
                'medium': 10,
                'high': 10
            }

            # Balance artist popularity
            balanced_artists = self.balance_artist_popularity(all_artists, target_popularity)

            # Writing to CSV
            headers = ['Category ID', 'Category Name', 'Playlist ID', 'Playlist Name', 'Artist Name', 'Artist Popularity']
            data = [[artist['category_id'], artist['category_name'], artist['playlist_id'], artist['playlist_name'],
                     artist['name'], artist['popularity']] for artist in balanced_artists]
            self.write_to_csv(output_file, data, headers)

        except Exception as e:
            print(f"An error occurred: {e}")

    # Package everything and run script directly (for testing)
    def main():
        # Replace 'your_client_id' and 'your_client_secret' with actual values
        client_id = 'your_client_id'
        client_secret = 'your_client_secret'
        
        # Initialize the SpotifyDataManager
        spotify_manager = SpotifyDataManager(client_id=client_id, client_secret=client_secret)
        
        # Fetch and save data to a CSV file
        spotify_manager.fetch_and_save_spotify_data()

    if __name__ == "__main__":
        main()