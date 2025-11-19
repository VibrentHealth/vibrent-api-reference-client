"""
Survey exporter for Vibrent Health API Client

This module contains the SurveyExporter class which handles survey-specific
export logic using the v1 API endpoint.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Survey, ExportRequest


class SurveyExporter(BaseExporter):
    """
    Exporter for survey data using the v1 API.

    This exporter fetches surveys, applies filtering based on configuration,
    and requests exports using the standard survey export endpoint.

    Configuration (in vibrent_config.yaml):
        export:
          survey:
            format: JSON  # or CSV
            request:
              max_surveys: null  # or number
              survey_ids: null  # or list of IDs
              exclude_survey_ids: null  # or list of IDs to exclude

    Usage:
        client = VibrentHealthAPIClient(config_manager)
        exporter = SurveyExporter(client, config_manager)
        surveys = exporter.get_items()
        filtered = exporter.filter_items(surveys)
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the survey exporter.

        Args:
            client: The API client instance
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger.info("Initialized SurveyExporter for v1 API")

    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        Returns:
            'survey'
        """
        return "survey"

    def get_items(self) -> List[Survey]:
        """
        Fetch available surveys from the API.

        Returns:
            List of Survey objects

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        self.logger.info("Fetching surveys from API")
        surveys = self.client.get_surveys()
        self.logger.info(f"Retrieved {len(surveys)} surveys")
        return surveys

    def filter_items(self, surveys: List[Survey]) -> List[Survey]:
        """
        Apply configuration-based filtering to surveys.

        Filtering logic:
        1. If survey_ids specified: only include those surveys
        2. If exclude_survey_ids specified: exclude those surveys
        3. If max_surveys specified: limit to that number

        Args:
            surveys: List of Survey objects to filter

        Returns:
            Filtered list of Survey objects
        """
        survey_filter = self.config_manager.get_survey_filter()
        max_surveys = survey_filter.get("max_surveys")

        filtered_surveys = []

        for survey in surveys:
            if self.config_manager.should_include_survey(survey.platformFormId, survey.name):
                filtered_surveys.append(survey)

                # Check if we've reached the max
                if max_surveys and len(filtered_surveys) >= max_surveys:
                    self.logger.info(f"Reached max_surveys limit of {max_surveys}")
                    break

        self.logger.info(
            f"Filtered {len(surveys)} surveys down to {len(filtered_surveys)} "
            f"based on configuration"
        )

        return filtered_surveys

    def create_export_request(self, survey: Survey, date_range: Dict[str, int]) -> ExportRequest:
        """
        Create an export request for a survey.

        Args:
            survey: The Survey object to export
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            ExportRequest object configured for this survey
        """
        # Get format from survey-specific config, fallback to general export config
        survey_config = self.get_config_section()
        export_config = self.config_manager.get("export", {})

        export_format = survey_config.get("format") or export_config.get("format", "JSON")

        request = ExportRequest(
            dateFrom=date_range['start_time'],
            dateTo=date_range['end_time'],
            format=export_format
        )

        self.logger.debug(
            f"Created export request for survey {survey.platformFormId}: "
            f"format={export_format}, "
            f"dateFrom={date_range['start_time']}, "
            f"dateTo={date_range['end_time']}"
        )

        return request

    def request_export(self, survey: Survey, export_request: ExportRequest) -> str:
        """
        Request survey export via API.

        Args:
            survey: The Survey object being exported
            export_request: The ExportRequest object

        Returns:
            Export ID string

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        export_id = self.client.request_survey_export(survey.platformFormId, export_request)

        self.logger.debug(
            f"Requested export for survey {survey.platformFormId} "
            f"(Name: '{survey.name}'): export_id={export_id}"
        )

        return export_id

    def get_item_identifier(self, survey: Survey) -> str:
        """
        Get unique identifier for a survey.

        Args:
            survey: The Survey object

        Returns:
            String identifier (platform form ID)
        """
        return str(survey.platformFormId)

    def get_item_display_name(self, survey: Survey) -> str:
        """
        Get human-readable display name for a survey.

        Args:
            survey: The Survey object

        Returns:
            Formatted string with survey name and ID
        """
        return f"{survey.name} (ID: {survey.platformFormId})"

    def get_output_directory_name(self) -> str:
        """
        Get the output directory name for survey exports.

        Returns:
            Directory name (e.g., 'survey_exports')
        """
        output_config = self.config_manager.get_output_config()
        return output_config.get("survey_exports_dir", "survey_exports")
