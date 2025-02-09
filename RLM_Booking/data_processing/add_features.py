import math
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import regex as re
from integrations.artist_event_search import get_spotify_token, search_artist


#RLM/apps/data_processing
#need to add safety measures e.g. what to do if column alr exists

class AddFeatures:
    def __init__(self, df: pd.DataFrame = None, input_csv: str = None):
        """
        Initialize the ArtistParser either with a DataFrame or a CSV file path.

        :param df: pandas DataFrame containing the data.
        :param csv_path: Path to the CSV file to load data from.
        """
        load_dotenv()
        if df is not None and input_csv is not None:
            raise ValueError("Provide either a DataFrame or a CSV path, not both.")
        elif df is not None:
            self.df = df
        elif input_csv is not None:
            self.df = pd.read_csv(input_csv)
        else:
            raise ValueError("You must provide either a DataFrame or a CSV path.")
    

    @staticmethod
    def parse_artists(show):
        """
        Parse artist names from the 'Show' column based on specified patterns.

        NOTE: this function is imperfect, if its being used, please just use / to separate artists
        most ideally, just have a destinated column for artists in the csv
        """
        # Remove paranthesis and anything in them
        show_name = re.sub(r'\([^)]*\)', '', str(show)).strip()
        
        # Pattern -> description - A, B, C
        if ' - ' in show_name:
            parts = show_name.split(' - ', 1)
            artists_part = parts[1] if len(parts) > 1 else parts[0]
            artists = [artist.strip() for artist in artists_part.split(',')]
            return artists
        
        # Pattern -> A: description
        if ':' in show_name:
            artist = show_name.split(':', 1)[0].strip()
            return [artist]
        
        # Patterns with separators
        separators = [' / ', ' + ', ' w/ ', ' W/ ', ' & ', ' AND ', ' and ']
        for sep in separators:
            if sep in show_name:
                artists = [artist.strip() for artist in show_name.split(sep)]
                return artists
        
        # If no patterns matched, return the show_name as the artist
        return [show_name.strip()]
    

    @staticmethod
    def parse_custom_date(date_str):
        """
        Attempt to convert date_str into datetime using pandas' datetime inference
        """
        date_str = str(date_str).strip()
        if not date_str:
            return pd.NaT

        # Use pandas' datetime inference
        parsed_date = pd.to_datetime(date_str, infer_datetime_format=True, errors='coerce')
        return parsed_date if not pd.isnull(parsed_date) else pd.NaT


    @staticmethod
    def parse_currency(val):
        """
        Converts a string like "$5,808.00" to float 5808.0.
        If val is NaN or empty, returns NaN.
        """
        if pd.isnull(val) or str(val).strip() == '':
            return np.nan
        return float(str(val).replace('$', '').replace(',', ''))


    def add_artists(self):
        """
        Creates a new 'Artists' column, with artist names separated by commas, next to the 'Show' column
        
        NOTE: parse_artists is imperfet, most ideally, just have a destinated column for artists in the csv
        """
        if 'Artists' in self.df.columns:
            return
        
        if 'Artists' not in self.df.columns:
            # Create the 'Artists' series by applying parse_artists to each 'Show'
            artists_series = self.df['Show'].apply(lambda x: ', '.join(self.parse_artists(x)))
            
            # Find the position of 'Show' and insert 'Artists' right after it
            show_position = self.df.columns.get_loc('Show')
            self.df.insert(show_position + 1, 'Artists', artists_series)


    def date_to_datetime(self):
        """
        Changes Date column to be in datetime format
        """
        self.df['Date'] = self.df['Date'].apply(self.parse_custom_date)


    def add_day_of_week(self):
        """
        Creates a 'Day of Week' column (Mon=1, Sun=7), inserts it after 'Date', then sorts by Date.
        """
        if 'Day of Week' in self.df.columns:
            return    
          
        self.df['Day of Week'] = self.df['Date'].dt.dayofweek + 1
        
        date_idx = self.df.columns.get_loc('Date')
        self.df.insert(date_idx+1, 'Day of Week', self.df.pop('Day of Week'))
        self.df.sort_values(by="Date", inplace=True)


    def add_cyclical_features(self, use_two_sine_signal=False):
        """
        Adds cyclical features for day-of-year and (optionally) a synthetic 2-sine signal.
        Also adds cyclical features for day-of-week.
        
        :param use_two_sine_signal: if True, creates a '2sine_day_of_year' column
                                    combining two sine waves. 
        """
        if 'Days Elapsed' in self.df.columns:
            return

        self.df["Days Elapsed"] = (self.df["Date"] - self.df["Date"].min()).dt.days # day_nr = days since earliest date
        self.df["Day of Year"] = self.df["Date"].dt.day_of_year 
        
        # sin/cos of day_of_year (1..365)
        self.df["Sin Day of Year"] = np.sin(2 * np.pi * self.df["Day of Year"] / 365)
        self.df["Cos Day of Year"] = np.cos(2 * np.pi * self.df["Day of Year"] / 365)
        
        # sin/cos of day_of_week (Mon=1..Sun=7 => shift by -1 => 0..6)
        self.df["Sin Day of Week"] = np.sin(2 * np.pi * (self.df["Day of Week"] - 1) / 7)
        self.df["Cos Day of Week"] = np.cos(2 * np.pi * (self.df["Day of Week"] - 1) / 7)
        
        # synthetic 2-sine wave feature
        if use_two_sine_signal:
            signal_1 = 3 + 4 * np.sin(self.df["Days Elapsed"] / 365 * 2 * np.pi)
            signal_2 = 3 * np.sin(self.df["Days Elapsed"] / 365 * 4 * np.pi + 365/2)
            self.df["2Sine Day Of Year"] = signal_1 + signal_2
        
        date_idx = self.df.columns.get_loc('Date') 
        self.df.insert(date_idx+1, 'Days Elapsed', self.df.pop('Days Elapsed'))
        self.df.insert(date_idx+2, 'Day of Year', self.df.pop('Day of Year'))
        self.df.insert(date_idx+3, 'Sin Day of Year', self.df.pop('Sin Day of Year'))
        self.df.insert(date_idx+4, 'Cos Day of Year', self.df.pop('Cos Day of Year'))
        self.df.insert(date_idx+5, '2Sine Day Of Year', self.df.pop('2Sine Day Of Year'))
        
        dow_idx = self.df.columns.get_loc('Day of Week')
        self.df.insert(dow_idx+1, 'Sin Day of Week', self.df.pop('Sin Day of Week'))
        self.df.insert(dow_idx+2, 'Cos Day of Week', self.df.pop('Cos Day of Week'))


    def add_gbor_bar_sales_ratio(self):
        """
        Creates numeric columns for Total GBOR & Bar Sales
        Adds GBOR_Bar_Sales_Ratio column = Total_GBOR_numeric / Bar_Sales_numeric.
        """
        if 'GBOR Bar Sales Ratio' in self.df.columns:
            return

        self.df["Total GBOR Numeric"] = self.df["Total GBOR"].apply(self.parse_currency)
        self.df["Bar Sales Numeric"] = self.df["Bar Sales"].apply(self.parse_currency)
        
        self.df["Bar Sales Numeric"] = self.df["Bar Sales Numeric"].replace(0, np.nan)
        
        self.df["GBOR Bar Sales Ratio"] = (
            self.df["Total GBOR Numeric"] / self.df["Bar Sales Numeric"]
        )
        
        gbor_idx = self.df.columns.get_loc('Total GBOR')
        self.df.insert(gbor_idx+1, 'Total GBOR Numeric', self.df.pop('Total GBOR Numeric'))
        
        bar_idx = self.df.columns.get_loc('Bar Sales')
        self.df.insert(bar_idx+1, 'Bar Sales Numeric', self.df.pop('Bar Sales Numeric'))
        self.df.insert(bar_idx+2, 'GBOR Bar Sales Ratio', self.df.pop('GBOR Bar Sales Ratio'))


    @staticmethod
    def get_max(x):
        parts = str(x).split(',')
        numbers = [int(part) for part in parts]
        return max(numbers)

    def add_spotify_followers_column(self):
        """
        Creates 2 columns
            Spotify Followers: artist's Spotify follower counts. Separated by comma if there are multiple artists
            Spotify Followers Max: largest followers count in Spotify Followers
        """
        if 'Spotify Followers' in self.df.columns:
            return

        token = get_spotify_token()
        followers_list = []
        # count = 0

        for idx, row in self.df.iterrows():
            artist_names = [item.strip() for item in row['Artists'].split(',')]
            # print(f"Row {idx} items: {artist_names}")
            followers = []
            for artist in artist_names:
                artist_data = search_artist(artist, token)
                try:
                    followers_total = artist_data['artists']['items'][0]['followers']['total']
                    # If the field is empty (e.g., empty string or None), set to NaN
                    if followers_total in ("", None):
                        followers_total = math.nan
                except (KeyError, IndexError, TypeError):
                    followers_total = math.nan
                followers.append(followers_total)
                # print(artist_data)
            comma_separated = ",".join(map(str, followers))
            followers_list.append(comma_separated)
            
        self.df["Spotify Followers"] = followers_list
        self.df['Spotify Followers Max'] = self.df['Spotify Followers'].apply(self.get_max)



    def add_spotify_genre_column(self):
        '''
        Retrive the genres of all artists in a comma separated format
        '''
        if 'Combined Genres' in self.df.columns:
            return

        token = get_spotify_token()
        combined_genres_list = []

        for idx, row in self.df.iterrows():
            artist_names = [item.strip() for item in row['Artists'].split(',')]
            all_genres = []
            
            for artist in artist_names:
                try:
                    artist_data = search_artist(artist, token)
                    # Extract genres from the first search result.
                    genres = artist_data['artists']['items'][0]['genres']
                except (IndexError, KeyError):
                    print(f"Error retrieving genres for artist: {artist}")
                    genres = []
                all_genres.extend(genres)

            combined_genres = list(set(all_genres))
            combined_genres_cs = ",".join(combined_genres)
            combined_genres_list.append(combined_genres_cs)
        
        self.df['Combined Genres'] = combined_genres_list


    def save_data(self, output_csv: str):
        """
        Saves the current DataFrame to the specified CSV path.
        """
        self.df.to_csv(output_csv, index=False)
        print(f"Data saved to {output_csv}")


    def run_pipeline(self, output_csv: str, use_two_sine_signal: bool = False):
        """
        Convenience method to run all steps in one call:
          1) Add artists
          2) change date to datetime format
          3) Add day_of_week
          4) Add cyclical features (optionally with 2 sine signals)
          5) Add GBOR-Bar Sales ratio
          6) Add Spotify follower columns
          7) Add Spotify genre columns
          8) Save final CSV
        """
        self.add_artists()
        self.date_to_datetime()
        self.add_day_of_week()
        self.add_cyclical_features(use_two_sine_signal=use_two_sine_signal)
        self.add_gbor_bar_sales_ratio()
        self.add_spotify_followers_column()
        self.add_spotify_genre_column()
        self.save_data(output_csv)