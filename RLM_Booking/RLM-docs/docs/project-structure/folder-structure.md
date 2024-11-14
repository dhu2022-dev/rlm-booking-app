# Folder Structure

This section provides an overview of the main folders and files in the project, explaining their purpose and organization.

## Root Directory

- **/RLM-docs**: Documentation directory.
    - **/docs**: Contains all documentation files organized into specific topics like API, AWS, database, deployment, and features.
    - **mkdocs.yml**: Configuration file for generating the documentation site with MKDocs.

- **/RLM_Booking_Main**: Django project root.
    - **settings.py**: Global settings for the Django project, including database configurations, middleware, and installed apps.
    - **urls.py**: Defines URL routing for the project.
    - **wsgi.py / asgi.py**: Interfaces for serving the application.

- **/apps**: Contains Django apps grouped by functionality.
    - **/artist_recommendation**: App handling artist recommendations.
        - **models.py**: Defines database models.
        - **views.py**: Manages HTTP responses for artist recommendation.
        - **urls.py**: Routes URLs specific to artist recommendations.
    - **/concert_performance**: Manages data and views related to concert performance analysis.
    - **/event_management**: Provides functionality for event tracking and management.
    - **/marketing_tools**: App dedicated to marketing and promotional tools.

- **/data_processing**: Contains data processing services and utilities.
    - **services.py**: Primary service functions for data processing.
    - **/utils**: Helper scripts like `data_writer.py` and `progress_manager.py` for handling data output and tracking.

- **/integrations**: Manages external data sources and APIs.
    - **spotify_data_manager.py**: Connects and manages data from Spotify.
    - **ticketmaster_to_csv.py**: Handles integration with Ticketmaster API to retrieve and export data.

- **/shared_services**: Contains utilities and shared services for AWS and logging.
    - **aws_database_manager.py**: Manages AWS database connections and interactions.
    - **geolocation.py**: Provides geolocation services.
    - **logging_manager.py**: Configures and manages logging across the project.

- **/static**: Stores static assets like CSS, JavaScript, and images for frontend rendering.

- **/templates**: HTML templates for frontend views.
    - **base.html**: Base template for page structure.
    - **artist_recommendation/index.html**: Specific template for the artist recommendation page.

Each folder has been organized to facilitate efficient development, testing, and deployment. For detailed explanations of each folder's purpose, refer to the **Key Modules** section.
