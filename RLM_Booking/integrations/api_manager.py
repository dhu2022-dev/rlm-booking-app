import requests
import base64
import logging
import time
from typing import Dict, Any, Optional

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
        Supports 'Bearer' and 'Basic' authentication schemes.
        """
        if self.auth_type == 'Bearer' and 'client_id' in self.credentials and 'client_secret' in self.credentials:
            self.access_token = self.get_oauth_token()
            self.headers = {'Authorization': f'Bearer {self.access_token}'}
        elif self.auth_type == 'Basic' and 'username' in self.credentials and 'password' in self.credentials:
            auth_str = f"{self.credentials['username']}:{self.credentials['password']}"
            self.headers = {'Authorization': f"Basic {base64.b64encode(auth_str.encode()).decode()}"}
        elif self.auth_type == 'APIKey' and 'apikey' in self.credentials:
            self.params['apikey'] = self.credentials['apikey']
        else:
            logging.error("Unsupported authentication type or missing credentials.")

    def get_oauth_token(self) -> str:
        """
        Retrieves an OAuth token using client credentials for APIs that support OAuth2.
        
        Returns:
            str: The access token.
        """
        logging.debug("Getting OAuth token.")
        
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
            logging.error(f"Failed to retrieve OAuth token: {e}")
            return ''

    def make_request(self, endpoint: str, method: str = 'GET', params: Optional[Dict[str, Any]] = {}) -> Dict[str, Any]:
        """
        Makes a request to the API with automatic token refresh and rate limit handling.

        Args:
            endpoint (str): The specific endpoint of the API.
            method (str): The HTTP method, default is 'GET'.
            params (Optional[Dict[str, Any]]): Query parameters or payload for the request.

        Returns:
            dict: JSON response data from the API or an empty dict on failure.
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            # Apply a short delay to avoid rate limits
            time.sleep(0.3)

            params.update(self.params) #add on request paramaters to initial parameters, needed if apikey is a param

            response = requests.request(method, url, headers=self.headers, params=params if method == 'GET' else None, json=params if method != 'GET' else None)

            # Refresh token if unauthorized
            if response.status_code == 401 and self.auth_type == 'Bearer':
                logging.info("Access token expired. Refreshing...")
                self.authenticate()
                response = requests.request(method, url, headers=self.headers, params=params)

            # Handle rate limits by retrying after the specified delay
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))
                logging.warning(f"Rate limit reached. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self.make_request(endpoint, method, params)

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return {}
