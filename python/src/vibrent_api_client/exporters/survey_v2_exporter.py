"""
Survey V2 exporter for Vibrent Health API Client

This module contains the SurveyV2Exporter class which handles survey exports
using the V2 API endpoint with advanced features like wide format reporting,
PII removal, and data dictionary inclusion.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Survey, WideFormatReportRequest


class SurveyV2Exporter(BaseExporter):
    """
    Exporter for survey data using the V2 API with wide format support.

    The V2 API provides enhanced export capabilities:
    - Wide format reporting with one row per participant
    - Data dictionary inclusion
    - PII removal options
    - Custom choice value formats (value only, text only, or both)
    - User type filtering (real users, test users, or all)
    - Completed-only or all responses
    - Custom filename prefixes

    Configuration (in vibrent_config.yaml):
        export:
          survey_v2:
            file_type: CSV  # or JSON
            remove_pii: false
            completed_only: true
            include_withdrawn_user: true
            combine_values_for_multiple_choices: true
            choice_value_format: VALUE_AND_TEXT  # VALUE_ONLY, TEXT_ONLY, VALUE_AND_TEXT
            user_type: REAL_ONLY  # REAL_ONLY, TEST_ONLY, ALL_USERS
            request:
              max_surveys: null
              survey_ids: null
              exclude_survey_ids: null

    Usage:
        client = VibrentHealthAPIClient(config_manager)
        exporter = SurveyV2Exporter(client, config_manager)
        surveys = exporter.get_items()
        filtered = exporter.filter_items(surveys)
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the Survey V2 exporter.

        Args:
            client: The API client instance
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger.info("Initialized SurveyV2Exporter for V2 API with wide format support")

    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        Returns:
            'survey_v2'
        """
        return "survey_v2"

    def get_items(self) -> List[Survey]:
        """
        Fetch available surveys from the API.

        Note: V2 API uses the same survey listing endpoint as V1.

        Returns:
            List of Survey objects

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        self.logger.info("Fetching surveys from API (V2 uses same survey list as V1)")
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

        Note: V2 uses the same filtering as V1, but with survey_v2 config section.

        Args:
            surveys: List of Survey objects to filter

        Returns:
            Filtered list of Survey objects
        """
        # Get V2-specific config section
        v2_config = self.get_config_section()
        request_config = v2_config.get("request", {})

        max_surveys = request_config.get("max_surveys")
        survey_ids = request_config.get("survey_ids")
        exclude_survey_ids = request_config.get("exclude_survey_ids")

        filtered_surveys = []

        for survey in surveys:
            # Check inclusion list
            if survey_ids is not None:
                if survey.platformFormId not in survey_ids:
                    self.logger.debug(f"Skipping survey {survey.platformFormId} - not in survey_ids list")
                    continue

            # Check exclusion list
            if exclude_survey_ids is not None:
                if survey.platformFormId in exclude_survey_ids:
                    self.logger.debug(f"Skipping survey {survey.platformFormId} - in exclude_survey_ids list")
                    continue

            filtered_surveys.append(survey)

            # Check max limit
            if max_surveys and len(filtered_surveys) >= max_surveys:
                self.logger.info(f"Reached max_surveys limit of {max_surveys}")
                break

        self.logger.info(
            f"Filtered {len(surveys)} surveys down to {len(filtered_surveys)} "
            f"based on V2 configuration"
        )

        return filtered_surveys

    def create_export_request(self, survey: Survey, date_range: Dict[str, int]) -> WideFormatReportRequest:
        """
        Create a V2 export request for a survey with wide format options.

        Args:
            survey: The Survey object to export
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            WideFormatReportRequest object configured for this survey
        """
        # Get V2-specific configuration
        v2_config = self.get_config_section()

        # Build request with all V2 options
        request = WideFormatReportRequest(
            dateFrom=date_range['start_time'],
            dateTo=date_range['end_time'],
            fileType=v2_config.get("file_type", "CSV"),
            removePII=v2_config.get("remove_pii", False),
            completedOnly=v2_config.get("completed_only", True),
            includeWithdrawnUser=v2_config.get("include_withdrawn_user", True),
            combineValuesForMultipleChoices=v2_config.get("combine_values_for_multiple_choices", True),
            choiceValueFormat=v2_config.get("choice_value_format", "VALUE_AND_TEXT"),
            userType=v2_config.get("user_type", "REAL_ONLY"),
        )

        self.logger.debug(
            f"Created V2 export request for survey {survey.platformFormId}: "
            f"fileType={request.fileType}, "
            f"removePII={request.removePII}, "
            f"completedOnly={request.completedOnly}, "
            f"userType={request.userType}, "
            f"choiceValueFormat={request.choiceValueFormat}"
        )

        return request

    def request_export(self, survey: Survey, export_request: WideFormatReportRequest) -> str:
        """
        Request survey export via V2 API.

        Args:
            survey: The Survey object being exported
            export_request: The WideFormatReportRequest object

        Returns:
            Export ID string

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        export_id = self.client.request_survey_v2_export(survey.platformFormId, export_request)

        self.logger.debug(
            f"Requested V2 export for survey {survey.platformFormId} "
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
            Formatted string with survey name and ID, indicating V2 export
        """
        return f"{survey.name} (ID: {survey.platformFormId}) [V2 Wide Format]"

    def get_output_directory_name(self) -> str:
        """
        Get the output directory name for Survey V2 exports.

        By default, V2 exports go to the same directory as V1 unless
        specifically configured otherwise.

        Returns:
            Directory name (e.g., 'survey_exports')
        """
        output_config = self.config_manager.get_output_config()

        # Check for V2-specific directory first
        v2_dir = output_config.get("survey_v2_exports_dir")
        if v2_dir:
            return v2_dir

        # Fall back to general survey directory
        return output_config.get("survey_exports_dir", "survey_exports")

    def validate_items(self, items: List[Survey]) -> bool:
        """
        Validate surveys for V2 export.

        Adds V2-specific validation on top of base validation.

        Args:
            items: List of Survey objects to validate

        Returns:
            True if items are valid for V2 export, False otherwise
        """
        # First run base validation
        if not super().validate_items(items):
            return False

        # V2-specific validations could go here
        # For example: check if surveys support wide format

        return True
