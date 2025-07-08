"""
Authentication manager for Vibrent Health APIs
"""

import logging
import os
import time

import requests
from requests.auth import HTTPBasicAuth

from .config import ConfigManager
from .constants import ErrorMessages, Headers, TimeConstants


class VibrentHealthAPIError(Exception):
    """Custom exception for Vibrent Health API errors"""
    pass


class AuthenticationManager:
    """Handles OAuth2 authentication for Vibrent Health APIs"""

    def __init__(self, config_manager: ConfigManager, environment: str = None):
        self.config_manager = config_manager
        self.environment = environment or config_manager.get("environment.default")
        self.client_id = os.getenv("VIBRENT_CLIENT_ID")
        self.client_secret = os.getenv("VIBRENT_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None

        if not self.client_id or not self.client_secret:
            raise VibrentHealthAPIError(ErrorMessages.MISSING_CREDENTIALS)

        # Get environment configuration
        env_config = self.config_manager.get_environment_config(self.environment)
        self.token_url = env_config.get("token_url")
        
        if not self.token_url:
            raise VibrentHealthAPIError(
                ErrorMessages.INVALID_ENVIRONMENT.format(environment=self.environment)
            )

        # Get auth configuration
        auth_config = self.config_manager.get("auth")
        self.timeout = auth_config.get("timeout", TimeConstants.DEFAULT_TIMEOUT)
        self.refresh_buffer = auth_config.get("refresh_buffer", TimeConstants.TOKEN_REFRESH_BUFFER)

        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> str:
        """Authenticate and get access token"""
        self.logger.info(f"Authenticating with {self.environment} environment")
        self.logger.info(f"Token URL: {self.token_url}")

        data = {
            "grant_type": "client_credentials"
        }

        self.logger.info(f"Client ID: {self.client_id}")
        self.logger.info(f"Client Secret: {self.client_secret[:8]}...")  # Only log first 8 chars for security

        try:
            response = requests.post(
                self.token_url,
                data=data,
                auth=HTTPBasicAuth(self.client_id, self.client_secret),
                headers={Headers.CONTENT_TYPE: Headers.APPLICATION_X_WWW_FORM_URLENCODED},
                timeout=self.timeout
            )

            # Log response details for debugging
            self.logger.info(f"Response status: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = time.time() + expires_in

                self.logger.info("Authentication successful")
                return self.access_token
            else:
                # Log error response for debugging
                try:
                    error_data = response.json()
                    self.logger.error(f"Authentication failed: {error_data}")
                except:
                    self.logger.error(f"Authentication failed: {response.text}")

                response.raise_for_status()

        except requests.RequestException as e:
            raise VibrentHealthAPIError(ErrorMessages.AUTHENTICATION_FAILED.format(error=str(e)))

    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        if not self.access_token or (self.token_expires_at and time.time() >= self.token_expires_at - self.refresh_buffer):
            self.authenticate()
        return self.access_token 