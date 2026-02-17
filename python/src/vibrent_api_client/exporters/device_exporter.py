"""
Device exporter for Vibrent Health API Client

This module contains the DeviceExporter class which handles device data
export logic for individual participants with optional filtering by device type
and data type.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Participant, DeviceDataExportRequest, DeviceType, DeviceDataType


class DeviceExporter(BaseExporter):
    """
    Exporter for device data (Fitbit, Garmin, Apple HealthKit).

    This exporter handles per-participant device data exports with optional filtering
    by device type (source), data type, and date range. Unlike survey exports which
    are survey-centric, device exports are participant-centric.

    Configuration (in vibrent_config.yaml):
        device_export:
          use_date_range: true
          date_range:
            default_days_back: 90
          split_date_range: true
          participant_ids: [12345, 67890]  # List of participant IDs
          max_participants: null  # or number to limit
          exclude_participant_ids: null  # or list of IDs to exclude
          device_types: ["FITBIT", "GARMIN"]  # Optional filter
          data_types: ["SLEEP", "HEART_RATE"]  # Optional filter
          manifest_only: false  # If true, export only manifest

    Usage:
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)
        participants = exporter.get_items()
        filtered = exporter.filter_items(participants)
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the device exporter.

        Args:
            client: The API client instance
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger.info("Initialized DeviceExporter")

    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        Returns:
            'device'
        """
        return "device"

    def get_items(self) -> List[Participant]:
        """
        Get list of participants from configuration.

        For device exports, participants are typically configured explicitly rather
        than fetched from an API, as device exports are done for specific participants.

        Returns:
            List of Participant objects

        Raises:
            ValueError: If no participant IDs are configured
        """
        self.logger.info("Loading participant list from configuration")

        # Get device-specific configuration
        device_config = self.get_config_section()

        # Get participant IDs from config
        participant_ids = device_config.get("participant_ids", [])

        if not participant_ids:
            error_msg = (
                "No participant IDs configured for device data export. "
                "Please specify participant_ids in device_export configuration."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Create Participant objects
        participants = [Participant(id=pid) for pid in participant_ids]

        self.logger.info(f"Loaded {len(participants)} participants for device data export")
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
        device_config = self.get_config_section()

        # Get filtering configuration
        exclude_ids = device_config.get("exclude_participant_ids", [])
        max_participants = device_config.get("max_participants")

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
    ) -> DeviceDataExportRequest:
        """
        Create a device data export request for a participant.

        Args:
            participant: The Participant object to export data for
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            DeviceDataExportRequest object configured for this participant
        """
        device_config = self.get_config_section()

        # Get device and data type filters from config
        device_types = device_config.get("device_types")
        data_types = device_config.get("data_types")
        manifest_only = device_config.get("manifest_only", False)

        # Convert empty lists to None (API expects null for "all types")
        if device_types is not None and len(device_types) == 0:
            device_types = None
        if data_types is not None and len(data_types) == 0:
            data_types = None

        # Validate device types if provided
        if device_types:
            invalid_types = [dt for dt in device_types if not DeviceType.is_valid(dt)]
            if invalid_types:
                self.logger.warning(
                    f"Invalid device types: {invalid_types}. "
                    f"Valid types: {DeviceType.get_all_types()}"
                )

        # Validate data types if provided
        if data_types:
            invalid_types = [dt for dt in data_types if not DeviceDataType.is_valid(dt)]
            if invalid_types:
                self.logger.warning(
                    f"Invalid data types: {invalid_types}. "
                    f"Valid types: {DeviceDataType.get_all_types()}"
                )

        # Extract date range values (can be None if date range is disabled)
        date_from = date_range.get('start_time')
        date_to = date_range.get('end_time')

        request = DeviceDataExportRequest(
            dateFrom=date_from,
            dateTo=date_to,
            deviceTypes=device_types,
            dataTypes=data_types,
            manifestOnly=manifest_only
        )

        self.logger.debug(
            f"Created device export request for participant {participant.id}: "
            f"dateFrom={date_from}, dateTo={date_to}, "
            f"deviceTypes={device_types}, dataTypes={data_types}, "
            f"manifestOnly={manifest_only}"
        )

        return request

    def request_export(
        self,
        participant: Participant,
        export_request: DeviceDataExportRequest
    ) -> str:
        """
        Request device data export via API.

        Args:
            participant: The Participant object whose data is being exported
            export_request: The DeviceDataExportRequest object

        Returns:
            Export ID string

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        export_id = self.client.request_device_export(participant.id, export_request)

        self.logger.debug(
            f"Requested device data export for participant {participant.id}: "
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
        Get the output directory name for device exports.

        Returns:
            Directory name (e.g., 'device_exports')
        """
        output_config = self.config_manager.get_output_config()
        return output_config.get("device_exports_dir", "device_exports")
