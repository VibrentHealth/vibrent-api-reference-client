"""
Main API client for Vibrent Health APIs
"""

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .auth import AuthenticationManager, VibrentHealthAPIError
from .config import ConfigManager
from .constants import APIEndpoints, ErrorMessages, Headers, TimeConstants
from ..models import Survey, ExportRequest, ExportStatus, WideFormatReportRequest
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
        self.debug_logging = api_config.get("debug_logging", False)

    def _log_request_debug(self, method: str, url: str, headers: Dict, body: Optional[Any] = None):
        """Log HTTP request details for debugging"""
        if not self.debug_logging:
            return

        self.logger.debug("=" * 80)
        self.logger.debug(f"HTTP REQUEST: {method} {url}")
        self.logger.debug("-" * 80)
        self.logger.debug(f"Headers: {json.dumps(headers, indent=2)}")

        if body is not None:
            if isinstance(body, dict):
                self.logger.debug(f"Body: {json.dumps(body, indent=2)}")
            else:
                self.logger.debug(f"Body: {str(body)}")
        else:
            self.logger.debug("Body: None")
        self.logger.debug("=" * 80)

    def _log_response_debug(self, response: requests.Response, error: bool = False):
        """Log HTTP response details for debugging"""
        if not self.debug_logging:
            return

        self.logger.debug("=" * 80)
        if error:
            self.logger.debug(f"HTTP RESPONSE (ERROR): {response.status_code if response else 'No Response'}")
        else:
            self.logger.debug(f"HTTP RESPONSE: {response.status_code}")
        self.logger.debug("-" * 80)

        if response is not None:
            self.logger.debug(f"Headers: {json.dumps(dict(response.headers), indent=2)}")

            try:
                # Try to parse as JSON for better formatting
                content = response.json()
                self.logger.debug(f"Body: {json.dumps(content, indent=2)}")
            except Exception:
                # If not JSON, log as text (truncate if too long)
                content = response.text
                if len(content) > 10000:
                    self.logger.debug(f"Body (truncated): {content[:10000]}... ({len(content)} total chars)")
                else:
                    self.logger.debug(f"Body: {content}")
        else:
            self.logger.debug("Body: No response received")

        self.logger.debug("=" * 80)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the API"""
        token = self.auth_manager.get_valid_token()
        headers = kwargs.get("headers", {})
        headers[Headers.AUTHORIZATION] = f"Bearer {token}"
        kwargs["headers"] = headers

        url = f"{self.base_url}{endpoint}"

        # Log request details if debug logging is enabled
        request_body = kwargs.get("json") or kwargs.get("data")
        self._log_request_debug(method, url, headers, request_body)

        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)

            # Log successful response
            self._log_response_debug(response, error=False)

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            # Log error response
            if hasattr(e, 'response') and e.response is not None:
                self._log_response_debug(e.response, error=True)

            error_content = ""
            if e.response is not None:
                try:
                    error_content = e.response.text
                except Exception:
                    pass
            raise VibrentHealthAPIError(
                ErrorMessages.API_REQUEST_FAILED.format(error=f"{str(e)}; Response content: {error_content}")
            )

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

        self.logger.info(f"Total surveys associated with this study: {len(surveys)}")
        return surveys

    def request_survey_export(self, survey_id: int, export_request: ExportRequest) -> str:
        """Request export for a specific survey (V1 API)"""
        response = self._make_request(
            "POST",
            APIEndpoints.EXPORT_REQUEST.format(survey_id=survey_id),
            json=asdict(export_request)
        )

        export_data = response.json()
        export_id = export_data["exportId"]

        return export_id

    def request_survey_v2_export(self, survey_id: int, export_request: WideFormatReportRequest) -> str:
        """
        Request export for a specific survey using V2 API with wide format support.

        The V2 API provides additional features:
        - Wide format reporting with data dictionary
        - PII removal options
        - Custom choice value formats
        - User type filtering (real, test, or all users)
        - Completed vs all responses

        Args:
            survey_id: The survey platform form ID
            export_request: WideFormatReportRequest with V2 options

        Returns:
            Export ID string to track the export status

        Raises:
            VibrentHealthAPIError: If API call fails

        Example:
            >>> request = WideFormatReportRequest(
            ...     dateFrom=1704067200000,
            ...     dateTo=1706745600000,
            ...     fileType="CSV",
            ...     removePII=True,
            ...     completedOnly=True
            ... )
            >>> export_id = client.request_survey_v2_export(1234, request)
        """
        self.logger.info(f"Requesting Survey V2 export for survey {survey_id}")
        self.logger.debug(f"V2 Export options: fileType={export_request.fileType}, "
                         f"removePII={export_request.removePII}, "
                         f"completedOnly={export_request.completedOnly}, "
                         f"userType={export_request.userType}")

        response = self._make_request(
            "POST",
            APIEndpoints.EXPORT_REQUEST_V2.format(survey_id=survey_id),
            json=asdict(export_request)
        )

        export_data = response.json()
        export_id = export_data["exportId"]

        self.logger.info(f"Survey V2 export requested successfully: {export_id}")
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
