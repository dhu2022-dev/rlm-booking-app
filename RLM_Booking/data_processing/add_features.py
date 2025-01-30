import pandas as pd
import numpy as np
import regex as re

class AddFeatures:
    def __init__(self, df: pd.DataFrame = None, input_csv: str = None):
        """
        Initialize the ArtistParser either with a DataFrame or a CSV file path.

        :param df: pandas DataFrame containing the data.
        :param csv_path: Path to the CSV file to load data from.
        """
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
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
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
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        self.df["day_nr"] = (self.df["Date"] - self.df["Date"].min()).dt.days # day_nr = days since earliest date
        self.df["day_of_year"] = self.df["Date"].dt.day_of_year 
        
        # sin/cos of day_of_year (1..365)
        self.df["sin_day_of_year"] = np.sin(2 * np.pi * self.df["day_of_year"] / 365)
        self.df["cos_day_of_year"] = np.cos(2 * np.pi * self.df["day_of_year"] / 365)
        
        # sin/cos of day_of_week (Mon=1..Sun=7 => shift by -1 => 0..6)
        self.df["sin_day_of_week"] = np.sin(2 * np.pi * (self.df["Day of Week"] - 1) / 7)
        self.df["cos_day_of_week"] = np.cos(2 * np.pi * (self.df["Day of Week"] - 1) / 7)
        
        # synthetic 2-sine wave feature
        if use_two_sine_signal:
            signal_1 = 3 + 4 * np.sin(self.df["day_nr"] / 365 * 2 * np.pi)
            signal_2 = 3 * np.sin(self.df["day_nr"] / 365 * 4 * np.pi + 365/2)
            self.df["2sine_day_of_year"] = signal_1 + signal_2
        
        date_idx = self.df.columns.get_loc('Date') 
        self.df.insert(date_idx+1, 'day_nr', self.df.pop('day_nr'))
        self.df.insert(date_idx+2, 'day_of_year', self.df.pop('day_of_year'))
        self.df.insert(date_idx+3, 'sin_day_of_year', self.df.pop('sin_day_of_year'))
        self.df.insert(date_idx+4, 'cos_day_of_year', self.df.pop('cos_day_of_year'))
        self.df.insert(date_idx+5, '2sine_day_of_year', self.df.pop('2sine_day_of_year'))
        
        dow_idx = self.df.columns.get_loc('Day of Week')
        self.df.insert(dow_idx+1, 'sin_day_of_week', self.df.pop('sin_day_of_week'))
        self.df.insert(dow_idx+2, 'cos_day_of_week', self.df.pop('cos_day_of_week'))


    def add_gbor_bar_sales_ratio(self):
        """
        Creates numeric columns for Total GBOR & Bar Sales
        Adds GBOR_Bar_Sales_Ratio column = Total_GBOR_numeric / Bar_Sales_numeric.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        self.df["Total_GBOR_numeric"] = self.df["Total GBOR"].apply(self.parse_currency)
        self.df["Bar_Sales_numeric"] = self.df["Bar Sales"].apply(self.parse_currency)
        
        self.df["Bar_Sales_numeric"] = self.df["Bar_Sales_numeric"].replace(0, np.nan)
        
        self.df["GBOR_Bar_Sales_Ratio"] = (
            self.df["Total_GBOR_numeric"] / self.df["Bar_Sales_numeric"]
        )
        
        gbor_idx = self.df.columns.get_loc('Total GBOR')
        self.df.insert(gbor_idx+1, 'Total_GBOR_numeric', self.df.pop('Total_GBOR_numeric'))
        
        bar_idx = self.df.columns.get_loc('Bar Sales')
        self.df.insert(bar_idx+1, 'Bar_Sales_numeric', self.df.pop('Bar_Sales_numeric'))
        self.df.insert(bar_idx+2, 'GBOR_Bar_Sales_Ratio', self.df.pop('GBOR_Bar_Sales_Ratio'))


    def save_data(self, output_csv: str):
        """
        Saves the current DataFrame to the specified CSV path.
        """
        if self.df is None:
            raise ValueError("Nothing to save; self.df is empty.")
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
          6) Save final CSV
        """
        self.add_artists()
        self.date_to_datetime()
        self.add_day_of_week()
        self.add_cyclical_features(use_two_sine_signal=use_two_sine_signal)
        self.add_gbor_bar_sales_ratio()
        self.save_data(output_csv)