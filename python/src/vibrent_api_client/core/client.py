"""
Main API client for Vibrent Health APIs
"""

import logging
from dataclasses import asdict
from pathlib import Path
from typing import List

import requests

from .auth import AuthenticationManager, VibrentHealthAPIError
from .config import ConfigManager
from .constants import APIEndpoints, ErrorMessages, Headers, TimeConstants
from ..models import Survey, ExportRequest, ExportStatus
from ..utils.helpers import safe_from_dict


class VibrentHealthAPIClient:
    """Main client for interacting with Vibrent Health APIs"""

    def __init__(self, config_manager: ConfigManager, environment: str = None):
        self.config_manager = config_manager
        self.environment = environment or config_manager.get("environment.default")
        self.auth_manager = AuthenticationManager(config_manager, self.environment)
        self.logger = logging.getLogger(__name__)

        # Get environment configuration
        env_config = self.config_manager.get_environment_config(self.environment)
        self.base_url = env_config.get("base_url")

        if not self.base_url:
            raise VibrentHealthAPIError(
                ErrorMessages.INVALID_ENVIRONMENT.format(environment=self.environment)
            )

        # Get API configuration
        api_config = self.config_manager.get("api")
        self.timeout = api_config.get("timeout", TimeConstants.DEFAULT_TIMEOUT)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the API"""
        token = self.auth_manager.get_valid_token()
        headers = kwargs.get("headers", {})
        headers[Headers.AUTHORIZATION] = f"Bearer {token}"
        kwargs["headers"] = headers

        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise VibrentHealthAPIError(ErrorMessages.API_REQUEST_FAILED.format(error=str(e)))

    def get_surveys(self) -> List[Survey]:
        """Get list of available surveys"""
        self.logger.info("Fetching surveys")
        response = self._make_request("GET", APIEndpoints.SURVEYS)

        surveys_data = response.json()
        surveys = []
        for i, survey_data in enumerate(surveys_data):
            try:
                survey = safe_from_dict(Survey, survey_data, self.logger)
                surveys.append(survey)
            except Exception as e:
                self.logger.warning(f"Failed to create Survey object from data at index {i}: {e}")
                self.logger.debug(f"Survey data: {survey_data}")
                continue

        self.logger.info("Total surveys associated with this study: {}", len(surveys))
        return surveys

    def request_survey_export(self, survey_id: int, export_request: ExportRequest) -> str:
        """Request export for a specific survey"""
        response = self._make_request(
            "POST",
            APIEndpoints.EXPORT_REQUEST.format(survey_id=survey_id),
            json=asdict(export_request)
        )

        export_data = response.json()
        export_id = export_data["exportId"]

        return export_id

    def get_export_status(self, export_id: str) -> ExportStatus:
        """Get status of an export request"""
        response = self._make_request("GET", APIEndpoints.EXPORT_STATUS.format(export_id=export_id))
        status_data = response.json()
        return safe_from_dict(ExportStatus, status_data, self.logger)

    def download_export(self, export_id: str, output_path: Path) -> Path:
        response = self._make_request("GET", APIEndpoints.EXPORT_DOWNLOAD.format(export_id=export_id))
        filename = f"export_{export_id}.zip"
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition and "filename=" in content_disposition:
            filename = export_id + '_' + content_disposition.split("filename=")[1].strip('"')

        file_path = output_path / filename

        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
