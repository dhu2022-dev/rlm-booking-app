import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

from api_manager import APIManager  
from progress_manager import ProgressManager  
from data_writer import DataWriter  

#logging and stuff
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class PollstarDataManager:
    def __init__(self, api_manager: APIManager):
        """
        Initializes the PollstarDataManager with an APIManager instance.

        Args:
            api_manager (APIManager): An instance of APIManager to manage API requests.
        """
        self.api_manager = api_manager

    def get_artist_id(self, artist_name: str) -> str:
        """
        Searches for an artist by name using the Pollstar API and returns the artist's unique ID.

        Args:
            artist_name (str): The name of the artist to search for.

        Returns:
            str: The unique ID of the artist.

        Raises:
            Exception: If the artist is not found or if the API response is invalid.
        """
        logging.debug(f"Searching for artist: {artist_name} in Pollstar API")

        response = self.api_manager.make_request("search", params={"q": artist_name})
        results = response.get("results", [])
        
        if not results:
            logging.error(f"No artist found with name: {artist_name}")
            raise Exception(f"No artist found with name: {artist_name}")
        
        # Assume the first result is the desired artist
        artist_id = results[0].get("id")
        if not artist_id:
            logging.error("Artist ID not found in the API response")
            raise Exception("Artist ID not found in the API response")
        
        logging.debug(f"Found artist ID: {artist_id} for artist: {artist_name}")
        return artist_id

    def fetch_box_office_data(self, artist_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the box office data for a given artist ID using the Pollstar API.

        Args:
            artist_id (str): The unique ID of the artist.

        Returns:
            List[Dict[str, Any]]: A list of box office records (dictionaries).
        """
        logging.debug(f"Fetching box office data for artist ID: {artist_id}")
        endpoint = f"artists/{artist_id}/boxoffice"
        response = self.api_manager.make_request(endpoint)
        # Assume the API returns a key "box_office_data" containing a list of records
        box_office_data = response.get("box_office_data", [])
        
        if not box_office_data:
            logging.info(f"No box office data found for artist ID: {artist_id}")
        else:
            logging.debug(f"Found {len(box_office_data)} box office record(s) for artist ID: {artist_id}")
        
        return box_office_data

    def fetch_and_save_pollstar_data(self, artist_name: str, data_writer: DataWriter, progress_manager: ProgressManager, data_point_limit: int = 10000):
        """
        Coordinates searching for an artist, fetching their box office data, and writing each record to CSV,
        while tracking progress.

        Args:
            artist_name (str): The name of the artist to search for.
            data_writer (DataWriter): Instance for writing data to CSV.
            progress_manager (ProgressManager): Instance for tracking progress.
            data_point_limit (int): Maximum number of data points to write.
        """
        logging.debug("Starting fetch_and_save_pollstar_data")
        data_points_collected = len(data_writer.existing_entries)

        try:
            artist_id = self.get_artist_id(artist_name)
            logging.info(f"Found artist ID: {artist_id} for {artist_name}")
        except Exception as e:
            logging.error(f"Error fetching artist ID for {artist_name}: {e}")
            return

        box_office_records = self.fetch_box_office_data(artist_id)
        if not box_office_records:
            logging.info(f"No box office data available for {artist_name}")
            return

        for record in box_office_records:
            # Assume each record contains fields such as "id", "event_date", "venue", "city", "revenue", and "attendance"
            record_id = record.get("id")
            if not record_id:
                logging.warning("Box office record missing 'id' field; skipping record.")
                continue

            # Use progress manager to potentially skip records already processed
            if progress_manager.should_skip(record_id, "box_office"):
                continue

            entry = {
                "artist_name": artist_name,
                "event_id": record_id,
                "event_date": record.get("event_date", "N/A"),
                "venue": record.get("venue", "N/A"),
                "city": record.get("city", "N/A"),
                "revenue": record.get("revenue", "N/A"),
                "attendance": record.get("attendance", "N/A")
            }

            if data_writer.write_entry_to_csv(entry):
                data_points_collected += 1
                logging.info(f"Box office record {record_id} for artist {artist_name} written to CSV.")
                progress_manager.save_progress(last_box_office_id=record_id)

            if data_points_collected >= data_point_limit:
                logging.info("Data point limit reached.")
                return


def main():
    load_dotenv()
    pollstar_api_key = os.getenv("POLLSTAR_API_KEY")
    
    if not pollstar_api_key:
        logging.error("POLLSTAR_API_KEY not found in environment variables.")
        return

    api_manager = APIManager(
        base_url="https://api.pollstar.com/boxoffice",
        auth_type="apikey",
        credentials={"api_key": pollstar_api_key}
    )

    pollstar_manager = PollstarDataManager(api_manager)
    data_writer = DataWriter("pollstar_box_office_data.csv", headers=["artist_name", "event_id", "event_date", "venue", "city", "revenue", "attendance"])
    progress_manager = ProgressManager("progress.json", progress_keys=["last_box_office_id"])

    # User Input
    artist_name = input("Enter the artist name to fetch box office data: ").strip()
    pollstar_manager.fetch_and_save_pollstar_data(artist_name, data_writer, progress_manager, data_point_limit=10000)


if __name__ == "__main__":
    main()
