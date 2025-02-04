import requests
import base64
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self, base_url: str, auth_type: Optional[str] = None, credentials: Optional[Dict[str, str]] = None):
        """
        Initializes APIManager with a base URL, optional authentication type, and credentials.

        Args:
            base_url (str): The base URL for the API.
            auth_type (Optional[str]): The type of authentication, e.g., 'Bearer' or 'Basic'.
            credentials (Optional[Dict[str, str]]): The credentials for authentication, such as client ID and secret.
        """
        self.base_url = base_url
        self.auth_type = auth_type
        self.credentials = credentials
        self.access_token = None
        self.headers = {}
        self.params = {}

        if auth_type and credentials:
            self.authenticate()

    def authenticate(self):
        """
        Handles authentication for the API based on the provided auth type and credentials.
        Supports 'Bearer', 'Basic', and API key authentication with customizable parameter names.
        """
        if self.auth_type == 'Bearer' and 'client_id' in self.credentials and 'client_secret' in self.credentials:
            self.access_token = self.get_oauth_token()
            self.headers = {'Authorization': f'Bearer {self.access_token}'}
        elif self.auth_type == 'Basic' and 'username' in self.credentials and 'password' in self.credentials:
            auth_str = f"{self.credentials['username']}:{self.credentials['password']}"
            self.headers = {'Authorization': f"Basic {base64.b64encode(auth_str.encode()).decode()}"}
        elif self.auth_type == 'APIKey' and 'api_key' in self.credentials:
            # Use a default key parameter name or a custom one if provided
            key_param_name = self.credentials.get('key_param_name', 'apikey')  # Default to 'apikey'
            self.params[key_param_name] = self.credentials['api_key']
        else:
            logger.error("Unsupported authentication type or missing credentials.")


    def get_oauth_token(self) -> str:
        """
        Retrieves an OAuth token using client credentials for APIs that support OAuth2.
        
        Returns:
            str: The access token.
        """
        logger.debug("Getting OAuth token.")
        
        auth_str = f"{self.credentials['client_id']}:{self.credentials['client_secret']}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        url = f"{self.base_url}/token"  # Adjust token URL if necessary
        headers = {'Authorization': f'Basic {b64_auth_str}'}
        data = {'grant_type': 'client_credentials'}
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json().get('access_token', '')
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve OAuth token: {e}")
            return ''

    def make_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict[str, Any]] = {}, raw_format: bool = False) -> Dict[str, Any]:
        """
        Makes a request to the API with manual encoding toggle.
        """
        # Remove trailing slash from base_url if it exists
        base_url = self.base_url.rstrip("/")
        url = f"{base_url}/{endpoint}".rstrip("/")  # Ensure no trailing slash

        try:
            # Add default parameters (e.g., API key)
            params.update(self.params)

            if raw_format:
                # Build query string manually for APIs requiring raw formats
                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                final_url = f"{url}?{query_string}"
            else:
                # Use requests to encode the query string
                final_url = url

            logger.debug(f"Final API Request URL: {final_url}")

            response = requests.request(
                method,
                final_url if raw_format else url,
                headers=self.headers,
                params=params if not raw_format and method == 'GET' else None,
                json=params if method != 'GET' else None,
            )

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {}
