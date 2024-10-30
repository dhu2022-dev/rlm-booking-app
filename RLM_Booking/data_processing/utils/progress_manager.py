import json
import logging
from typing import Optional, List, Dict

class ProgressManager:
    def __init__(self, progress_file: str, progress_keys: List[str]):
        """
        Initializes ProgressManager with a file path and keys for progress tracking.
        
        Args:
            progress_file (str): Path to the JSON file for saving progress.
            progress_keys (List[str]): List of keys to track progress (e.g., ['last_category_id', 'last_playlist_id', 'last_track_id']).
        """
        self.progress_file = progress_file
        self.progress_keys = progress_keys
        self.progress = self.load_progress()

    def load_progress(self) -> Dict[str, Optional[str]]:
        """
        Loads the last saved progress from the progress file if it exists.
        
        Returns:
            dict: A dictionary with progress tracking keys set to last known values.
        """
        try:
            with open(self.progress_file, 'r') as file:
                logging.debug(f"Loading progress from {self.progress_file}")
                return json.load(file)
        except FileNotFoundError:
            logging.info(f"Progress file {self.progress_file} not found. Starting fresh.")
            return {key: None for key in self.progress_keys}
        except json.JSONDecodeError:
            logging.error(f"Error decoding progress file {self.progress_file}. Starting fresh.")
            return {key: None for key in self.progress_keys}

    def save_progress(self, **kwargs) -> None:
        """
        Saves the current progress to the progress file.
        
        Args:
            kwargs: Keyword arguments corresponding to progress keys and their values.
        """
        for key in self.progress_keys:
            if key in kwargs:
                self.progress[key] = kwargs[key]
            else:
                logging.warning(f"Missing progress key: {key} in save_progress arguments.")
        
        with open(self.progress_file, 'w') as file:
            json.dump(self.progress, file)
        
        logging.debug(f"Progress saved: {self.progress}")

    def should_skip(self, current_id: str, level: str) -> bool:
        """
        Determines if an item should be skipped based on saved progress.
        
        Args:
            current_id (str): The current item's ID.
            level (str): The level key corresponding to the type of item (e.g., 'last_category_id').
        
        Returns:
            bool: True if the item should be skipped, False otherwise.
        """
        last_id = self.progress.get(f"last_{level}_id")
        if last_id and current_id != last_id:
            logging.debug(f"Skipping {level} with ID {current_id}")
            return True
        return False
