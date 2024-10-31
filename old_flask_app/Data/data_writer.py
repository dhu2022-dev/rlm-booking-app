import csv
import logging
from typing import Dict, Any, List, Set, Tuple

class DataWriter:
    def __init__(self, filename: str, headers: List[str]):
        """
        Initializes the DataWriter with a filename and headers for the CSV.
        
        Args:
            filename (str): Name of the CSV file to write data.
            headers (List[str]): List of header names for the CSV columns.
        """
        self.filename = filename
        self.headers = headers
        self.existing_entries = self.read_existing_entries()

    def read_existing_entries(self) -> Set[Tuple[str, ...]]:
        """
        Reads the CSV file to collect existing entries based on the headers,
        which helps avoid duplicates.
        
        Returns:
            Set[Tuple[str, ...]]: A set of tuples representing existing entries.
        """
        existing_entries = set()
        
        try:
            with open(self.filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Check if all expected columns are present
                if not set(self.headers).issubset(reader.fieldnames):
                    logging.error("CSV file is missing expected columns.")
                    return existing_entries
                
                for row in reader:
                    # Create a tuple based on the defined headers
                    entry = tuple(str(row[header]).strip() for header in self.headers)
                    existing_entries.add(entry)
                    
            logging.debug(f"Loaded {len(existing_entries)} existing entries from {self.filename}")
        
        except FileNotFoundError:
            logging.info(f"{self.filename} not found. A new file will be created.")
        
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
        
        return existing_entries

    def write_entry_to_csv(self, data: Dict[str, Any]) -> bool:
        """
        Writes a data entry to the CSV file if it is not a duplicate.
        
        Args:
            data (dict): A dictionary containing data to write. Must include all headers.
            
        Returns:
            bool: True if the data was written (not a duplicate), False otherwise.
        """
        # Create a tuple for duplicate checking based on the headers
        entry = tuple(str(data.get(header, '')).strip() for header in self.headers)
        
        # Check if the entry already exists
        if entry in self.existing_entries:
            logging.info(f"Duplicate entry found and skipped: {entry}")
            return False

        # Write the new entry to the CSV
        try:
            with open(self.filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                
                # Write the header if the file is new
                if file.tell() == 0:
                    writer.writeheader()
                
                writer.writerow({header: data.get(header, '') for header in self.headers})
                
            # Add the entry to the existing entries set
            self.existing_entries.add(entry)
            logging.debug(f"New entry added to CSV: {entry}")
            return True
        
        except Exception as e:
            logging.error(f"Error writing to CSV file: {e}")
            return False
