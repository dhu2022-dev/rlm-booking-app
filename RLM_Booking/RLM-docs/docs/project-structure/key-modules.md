# Key Modules

This section provides an overview of each main module and its purpose in the project. Modules are grouped by functionality to clarify their roles in the application. Each class and its methods are listed with a brief description. For even more specific information on the methods see the code comments.

---

## Data Processing Module

### Description

Handles backend data processing tasks, such as data cleaning and formatting, which support app functionalities like recommendation and event tracking.

### Key Components

- **services.py**: Main data processing functions.
- **/utils**: Supporting functions, including data writing and progress tracking.
    - **data_writer.py**: Helper class to scrape API data into a CSV. Takes in a filename and CSV headers; reads in any existing entries in a CSV and writes any new entries in that same CSV. read_existing_entries reads through the given csv and returns a list of items already inside. write_entry_to_csv writes in the entry if it is new; returns true if the entry to write was new and false if not.
    - **progress_manager.py**: Helper class to track the progress of API scraping to minimize API calls. Takes in a json file of the last API call stored and the headers of the data retrieved. Has load_progress which loads the API call progress stored in the JSON file. Has save_progress to record the last API call's info in the JSON file for future use. Has a should_skip method which checks if a potential call has already been made to reduce API calls.

## Frontend Module

### Description

The frontend module, defined within the `/static` and `/templates` folders, manages user interface elements like HTML, CSS, and JavaScript files, allowing users to interact with the backend data.

### Key Components

- **Templates**: HTML templates that render frontend views. Organized by Django app aka "feature".
- **Static Assets**: CSS for styling and JavaScript for interactive elements.

## Database Models Module

### Description

Defines Django models that handle the database schema and structure for data storage across different apps.

### Key Components

- **models.py**: Located in each app, it contains models defining the schema for artist recommendations, event management, concert performance, and marketing tools.
- **migrations**: Scripts to update database schema in response to changes in models.

## AWS Integration Module

### Description

Manages connections with AWS services for database storage, machine learning, and media handling.

### Key Components

- **aws_database_manager.py**: Connects with AWS databases like DynamoDB and S3.
- **geolocation.py**: Uses AWS location services to provide geolocation capabilities.
- **logging_manager.py**: Manages logging configurations, storing logs as needed for AWS services.

# API and Integrations Module

### Description

This module manages data communication both within the project (frontend and backend interactions) and with external APIs (e.g., Spotify, Ticketmaster). It includes the setup for API endpoints defined within each app (such as `artist_recommendation`, `concert_performance`) and manages integrations for retrieving and processing data from external sources.

### Key Components

- **Endpoints**: Defines API routes across various apps for internal data management, handling data for artist recommendations, event management, concert performance, and marketing tools.
- **api_manager.py**: A parent class that generalizes API setup, handling authentication, token management, and request processing for external services. Requires the base url for your API, an optional authentication type (i.e. Basic or Bearer), and any optional API credentials formatted in two string parameter dictionary where the keys might be something like [client_id, client_secret]. Has an authenticate method to authenticate your API connection based on authentication type (if specified). Has get_oath_token method which retrieves the oauth token using any client credentials. Has a refresh_token method to refresh the token if the current one is expired or invalid (for the APIs with temporary access tokens). 
- **spotify_data_manager.py**: Manages data retrieval and updates from Spotify, providing artist data for recommendations and analytics.
- **ticketmaster_to_csv.py**: Manages data retrieval from Ticketmaster, used for event listings and ticket information.

---
