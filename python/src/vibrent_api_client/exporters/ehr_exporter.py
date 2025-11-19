"""
EHR exporter for Vibrent Health API Client

This module contains the EHRExporter class which handles Electronic Health Record
(EHR) data export logic for individual participants.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Participant, EHRExportRequest


class EHRExporter(BaseExporter):
    """
    Exporter for Electronic Health Record (EHR) data.

    This exporter handles per-participant EHR data exports. Unlike survey exports
    which are survey-centric, EHR exports are participant-centric and export all
    EHR data for specified participants within a date range.

    Configuration (in vibrent_config.yaml):
        export:
          ehr:
            participant_ids: [12345, 67890]  # List of participant IDs
            max_participants: null  # or number to limit
            exclude_participant_ids: null  # or list of IDs to exclude

    Usage:
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)
        participants = exporter.get_items()
        filtered = exporter.filter_items(participants)
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the EHR exporter.

        Args:
            client: The API client instance
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger.info("Initialized EHRExporter")

    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        Returns:
            'ehr'
        """
        return "ehr"

    def get_items(self) -> List[Participant]:
        """
        Get list of participants from configuration.

        For EHR exports, participants are typically configured explicitly rather
        than fetched from an API, as EHR exports are done for specific participants.

        Returns:
            List of Participant objects

        Raises:
            ValueError: If no participant IDs are configured
        """
        self.logger.info("Loading participant list from configuration")

        # Get EHR-specific configuration
        ehr_config = self.get_config_section()

        # Get participant IDs from config
        participant_ids = ehr_config.get("participant_ids", [])

        if not participant_ids:
            error_msg = (
                "No participant IDs configured for EHR export. "
                "Please specify participant_ids in export.ehr configuration."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Create Participant objects
        participants = [Participant(id=pid) for pid in participant_ids]

        self.logger.info(f"Loaded {len(participants)} participants for EHR export")
        return participants

    def filter_items(self, participants: List[Participant]) -> List[Participant]:
        """
        Apply configuration-based filtering to participants.

        Filtering logic:
        1. If exclude_participant_ids specified: exclude those participants
        2. If max_participants specified: limit to that number

        Args:
            participants: List of Participant objects to filter

        Returns:
            Filtered list of Participant objects
        """
        ehr_config = self.get_config_section()

        # Get filtering configuration
        exclude_ids = ehr_config.get("exclude_participant_ids", [])
        max_participants = ehr_config.get("max_participants")

        filtered_participants = []

        for participant in participants:
            # Skip excluded participants
            if exclude_ids and participant.id in exclude_ids:
                self.logger.debug(f"Excluding participant {participant.id} (in exclusion list)")
                continue

            filtered_participants.append(participant)

            # Check if we've reached the max
            if max_participants and len(filtered_participants) >= max_participants:
                self.logger.info(f"Reached max_participants limit of {max_participants}")
                break

        self.logger.info(
            f"Filtered {len(participants)} participants down to {len(filtered_participants)} "
            f"based on configuration"
        )

        return filtered_participants

    def create_export_request(
        self,
        participant: Participant,
        date_range: Dict[str, int]
    ) -> EHRExportRequest:
        """
        Create an EHR export request for a participant.

        Args:
            participant: The Participant object to export data for
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            EHRExportRequest object configured for this participant
        """
        request = EHRExportRequest(
            dateFrom=date_range['start_time'],
            dateTo=date_range['end_time']
        )

        self.logger.debug(
            f"Created EHR export request for participant {participant.id}: "
            f"dateFrom={date_range['start_time']}, "
            f"dateTo={date_range['end_time']}"
        )

        return request

    def request_export(
        self,
        participant: Participant,
        export_request: EHRExportRequest
    ) -> str:
        """
        Request EHR data export via API.

        Args:
            participant: The Participant object whose data is being exported
            export_request: The EHRExportRequest object

        Returns:
            Export ID string

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        export_id = self.client.request_ehr_export(participant.id, export_request)

        self.logger.debug(
            f"Requested EHR export for participant {participant.id}: "
            f"export_id={export_id}"
        )

        return export_id

    def get_item_identifier(self, participant: Participant) -> str:
        """
        Get unique identifier for a participant.

        Args:
            participant: The Participant object

        Returns:
            String identifier (participant ID)
        """
        return str(participant.id)

    def get_item_display_name(self, participant: Participant) -> str:
        """
        Get human-readable display name for a participant.

        Args:
            participant: The Participant object

        Returns:
            Formatted string with participant ID
        """
        if participant.name:
            return f"Participant {participant.id} ({participant.name})"
        return f"Participant {participant.id}"

    def get_output_directory_name(self) -> str:
        """
        Get the output directory name for EHR exports.

        Returns:
            Directory name (e.g., 'ehr_exports')
        """
        output_config = self.config_manager.get_output_config()
        return output_config.get("ehr_exports_dir", "ehr_exports")
