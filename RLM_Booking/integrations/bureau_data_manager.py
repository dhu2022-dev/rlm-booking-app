import logging
from typing import Dict, Any
from dotenv import load_dotenv
import os
import requests
import json

from integrations.api_manager import APIManager  
from data_processing.utils.progress_manager import ProgressManager
from data_processing.utils.data_writer import DataWriter

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class BureauDataManager:
    def __init__(self, api_manager: APIManager):
        """
        Initializes the BureauDataManager with an APIManager instance.
        
        Args:
            api_manager (APIManager): An instance of APIManager to manage API requests.
        """
        self.api_manager = api_manager

    def get_census_groups(self) -> Dict[str, str]:
        # Step 1: Fetch all group codes dynamically
        try:
            groups_url = "https://api.census.gov/data/2020/acs/acs5/groups.json"
            groups_response = requests.get(groups_url)
            groups_response.raise_for_status()
            groups_metadata = groups_response.json()
            
            # Extract group codes
            group_codes = [group["name"] for group in groups_metadata["groups"]]
            logging.debug(f"Retrieved {len(group_codes)} groups from metadata.")
        except Exception as e:
            logging.error(f"Failed to fetch group metadata: {e}")
            return {"error": f"Failed to fetch group metadata: {e}"}

    def get_demographics(self, zip_code: str) -> Dict[str, Any]:
        """
        Fetch demographic data for a ZIP code using the Census API, split into multiple group-based calls.

        Args:
            zip_code (str): The ZIP code to query.

        Returns:
            dict: Combined demographic data or an error message.
        """
        logging.debug(f"Fetching demographics for ZIP code: {zip_code}")

        # Define groups of variables for separate calls
        groups = {
            "basic_info": ["NAME"],
            "population_by_sex": ["B01001_001E", "B01001_002E", "B01001_026E"],
            "age_distribution": [
                "B01001_003E", "B01001_004E", "B01001_005E", "B01001_006E",
                "B01001_007E", "B01001_008E", "B01001_009E", "B01001_010E",
                "B01001_011E", "B01001_012E", "B01001_013E", "B01001_014E",
                "B01001_015E", "B01001_016E", "B01001_017E", "B01001_018E",
                "B01001_019E", "B01001_020E", "B01001_021E", "B01001_022E"
            ],
            "race_distribution": [
                "B02001_002E", "B02001_003E", "B02001_004E", "B02001_005E",
                "B02001_006E", "B02001_007E", "B02001_008E", "B03001_003E"
            ],
            "income_housing": ["B19013_001E", "B25002_001E", "B25002_002E", "B25002_003E"]
        }

        # Initialize the result dictionary
        demographics = {"ZIP Code": zip_code}

        # Fetch data for each group and combine results
        for group_name, variables in groups.items():
            params = {
                "get": ",".join(variables),
                "for": f"zip code tabulation area:{zip_code}",
                "key": self.api_manager.credentials.get("api_key"),
            }

            try:
                # Call the API for the current group
                response = self.api_manager.make_request("", params=params, raw_format=True)

                if len(response) > 1:
                    # Map response into the demographics dictionary
                    header = response[0]
                    data = response[1]
                    group_data = {header[i]: data[i] for i in range(len(header))}
                    demographics.update(group_data)
                    logging.debug(f"Data fetched for group '{group_name}'")
                else:
                    logging.warning(f"No data found for group '{group_name}' in ZIP code {zip_code}")
            except Exception as e:
                logging.error(f"Error fetching data for group '{group_name}' in ZIP code {zip_code}: {e}")
                demographics[f"{group_name}_error"] = f"Error fetching data: {e}"

        return demographics

    def fetch_and_save_bureau_data(self, zip_code: str, output_file: str = "raw_demographics.json"):
        """
        Fetches demographic data for a ZIP code and saves the raw JSON response to a file.

        Args:
            zip_code (str): The ZIP code to process.
            output_file (str): The file where the raw JSON response will be saved.
        """
        logging.debug("Starting fetch_and_save_bureau_data")
        
        # Fetch demographic data
        demographics = self.get_demographics(zip_code)
        
        if "error" in demographics:
            logging.error(f"Error fetching demographics for {zip_code}: {demographics.get('error')}")
            return

        # Save the raw data as JSON
        try:
            with open(output_file, "w") as file:
                json.dump(demographics, file, indent=4)
            logging.info(f"Demographics data for ZIP code {zip_code} saved to {output_file}.")
        except Exception as e:
            logging.error(f"Failed to write demographics data for ZIP code {zip_code}: {e}")

    # def fetch_and_save_bureau_data(self, zip_code: str, data_writer: DataWriter, progress_manager: ProgressManager, data_point_limit: int = 10000):
    #     """
    #     Coordinates fetching demographic data for a ZIP code and saving it to CSV, 
    #     tracking progress as it goes.
        
    #     Args:
    #         zip_code (str): The ZIP code to process.
    #         data_writer (DataWriter): Instance for writing data to CSV.
    #         progress_manager (ProgressManager): Instance for tracking progress.
    #         data_point_limit (int): Maximum number of entries to write (if processing multiple ZIP codes).
    #     """
    #     logging.debug("Starting fetch_and_save_bureau_data")
    #     # Check if this ZIP code has already been processed.
    #     if progress_manager.should_skip(zip_code, "zip_code"):
    #         logging.info(f"ZIP code {zip_code} has already been processed. Skipping.")
    #         return

    #     demographics = self.get_demographics(zip_code)
    #     if "error" in demographics:
    #         logging.error(f"Error fetching demographics for {zip_code}: {demographics.get('error')}")
    #         return

    #     if data_writer.write_entry_to_csv(demographics):
    #         logging.info(f"Demographics data for ZIP code {zip_code} written to CSV.")
    #         progress_manager.save_progress(last_zip_code=zip_code)
    #     else:
    #         logging.error(f"Failed to write demographics data for ZIP code {zip_code}.")


def main():

    load_dotenv()
    census_api_key = os.getenv("CENSUS_API_KEY")
    
    if not census_api_key:
        logging.error("CENSUS_API_KEY not found in environment variables.")
        return

    api_manager = APIManager(
        base_url="https://api.census.gov/data/2020/acs/acs5",
        auth_type="APIKey",
        credentials={
            "apikey": census_api_key,
            "key_param_name": "key"  # Census-specific parameter name
        }
    )

    bureau_manager = BureauDataManager(api_manager)
    headers = [
        # Basic Location Info
        "ZIP Code",
        "Location Name",  # Census API returns "NAME"

        # Total Population
        "Total Population",  # B01001_001E

        # Gender Breakdown
        "Male Population",  # B01001_002E
        "Female Population",  # B01001_026E

        # Age Groups (Male & Female Combined)
        "Age Under 5",
        "Age 5 to 9",
        "Age 10 to 14",
        "Age 15 to 17",
        "Age 18 to 19",
        "Age 20 to 21",
        "Age 22 to 24",
        "Age 25 to 29",
        "Age 30 to 34",
        "Age 35 to 39",
        "Age 40 to 44",
        "Age 45 to 49",
        "Age 50 to 54",
        "Age 55 to 59",
        "Age 60 to 61",
        "Age 62 to 64",
        "Age 65 to 66",
        "Age 67 to 69",
        "Age 70 to 74",
        "Age 75 to 79",
        "Age 80 to 84",
        "Age 85 and over",

        # Race Breakdown (from B02001)
        "White Population",  # B02001_002E
        "Black or African American Population",  # B02001_003E
        "American Indian and Alaska Native Population",  # B02001_004E
        "Asian Population",  # B02001_005E
        "Native Hawaiian and Other Pacific Islander Population",  # B02001_006E
        "Some Other Race Population",  # B02001_007E
        "Two or More Races Population",  # B02001_008E

        # Hispanic/Latino Population (from B03001)
        "Hispanic or Latino Population",  # B03001_003E

        # Income (from B19013)
        "Median Household Income",  # B19013_001E

        # Urban Density (from B25002 - Housing Occupancy)
        "Total Housing Units",  # B25002_001E
        "Occupied Housing Units",  # B25002_002E
        "Vacant Housing Units"  # B25002_003E
    ]
    data_writer = DataWriter("bureau_data.csv", headers=headers)
    progress_manager = ProgressManager("progress.json", progress_keys=["last_zip_code"])

    # User input here
    zip_code = input("Enter the ZIP code for which you want demographic data: ").strip()
    output_file = f"raw_demographics_{zip_code}.json"  # Save each ZIP code's data in its own file
    bureau_manager.fetch_and_save_bureau_data(zip_code, output_file)



if __name__ == "__main__":
    main()
