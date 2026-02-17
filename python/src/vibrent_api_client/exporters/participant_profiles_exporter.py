"""
Participant Profiles exporter for Vibrent Health API Client

This module contains the ParticipantProfilesExporter class which handles
participant profile/user property data exports.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Participant, ParticipantProfilesExportRequest


class ParticipantProfilesExporter(BaseExporter):
    """
    Exporter for participant profiles (user properties) data.

    This exporter handles batch exports of participant profile data. Unlike other
    exporters that create one export per item, this creates a SINGLE export request
    for multiple participants.

    Special characteristics:
    - Batch export: One export request can include multiple participants (max 1000)
    - No date range: Always exports current participant data
    - No path parameter: POST to fixed endpoint, participants in request body
    - Special "export all" behavior: Empty participant_ids = export all participants

    Configuration (in vibrent_config.yaml):
        participant_profiles_export:
          # No date range - always exports current data
          use_date_range: false

          participant_ids: []  # Empty = export all, or list specific IDs
          max_participants: null  # Limit (API max is 1000)
          exclude_participant_ids: null  # IDs to exclude

    Usage:
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)
        participants = exporter.get_items()
        filtered = exporter.filter_items(participants)
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the participant profiles exporter.

        Args:
            client: The API client instance
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger.info("Initialized ParticipantProfilesExporter")

    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        Returns:
            'participant_profiles'
        """
        return "participant_profiles"

    def get_items(self) -> List[Participant]:
        """
        Get list of participants from configuration.

        For participant profiles, participants can be:
        1. Empty list [] -> export ALL participants (special behavior)
        2. List of IDs -> export only those participants

        Returns:
            List with single Participant object representing the batch export

        Note:
            This returns a list with ONE item that represents the batch export,
            not individual participants. This is because the API accepts a batch
            request for multiple participants.
        """
        self.logger.info("Loading participant configuration")

        # Get participant profiles-specific configuration
        profiles_config = self.get_config_section()

        # Get participant IDs from config
        participant_ids = profiles_config.get("participant_ids", [])

        if participant_ids is None or len(participant_ids) == 0:
            # Empty or null = export ALL participants
            self.logger.info("Configuration set to export ALL participants")
            # Create a special marker participant to represent "all participants"
            return [Participant(id=0, name="All Participants")]
        else:
            # Export specific participants - create single batch item
            self.logger.info(f"Configuration set to export {len(participant_ids)} specific participants")
            # Store the participant IDs in a single Participant object's external_id field
            # We'll extract these later in create_export_request
            batch_participant = Participant(
                id=0,
                name=f"Batch Export ({len(participant_ids)} participants)"
            )
            # Store the IDs as a custom attribute (will be used in create_export_request)
            batch_participant.batch_participant_ids = participant_ids
            return [batch_participant]

    def filter_items(self, participants: List[Participant]) -> List[Participant]:
        """
        Apply configuration-based filtering to participants.

        For participant profiles, this validates:
        1. Maximum participants limit (API max is 1000)
        2. Exclusions (if specified)

        Args:
            participants: List with single Participant representing batch export

        Returns:
            Filtered list (usually same single item, or empty if all excluded)
        """
        if not participants:
            return []

        profiles_config = self.get_config_section()
        batch_participant = participants[0]

        # Get the original participant IDs from config
        participant_ids = profiles_config.get("participant_ids", [])

        # If exporting all participants, no filtering needed
        if not participant_ids:
            self.logger.info("Exporting all participants - no filtering applied")
            return participants

        # Apply exclusions
        exclude_ids = profiles_config.get("exclude_participant_ids", [])
        if exclude_ids:
            original_count = len(participant_ids)
            participant_ids = [pid for pid in participant_ids if pid not in exclude_ids]
            excluded_count = original_count - len(participant_ids)
            if excluded_count > 0:
                self.logger.info(f"Excluded {excluded_count} participant(s) from export")

        # Apply max_participants limit
        max_participants = profiles_config.get("max_participants")
        if max_participants and len(participant_ids) > max_participants:
            self.logger.info(f"Limiting to first {max_participants} participants (was {len(participant_ids)})")
            participant_ids = participant_ids[:max_participants]

        # Validate API limit (1000 participants max)
        if len(participant_ids) > 1000:
            self.logger.error(
                f"Participant count ({len(participant_ids)}) exceeds API limit of 1000. "
                f"Truncating to first 1000 participants."
            )
            participant_ids = participant_ids[:1000]

        # Update the batch participant with filtered IDs
        if participant_ids:
            batch_participant.batch_participant_ids = participant_ids
            batch_participant.name = f"Batch Export ({len(participant_ids)} participants)"
            self.logger.info(
                f"After filtering: {len(participant_ids)} participant(s) to export"
            )
            return [batch_participant]
        else:
            self.logger.warning("All participants were filtered out - no export will be created")
            return []

    def create_export_request(
        self,
        participant: Participant,
        date_range: Dict[str, int]
    ) -> ParticipantProfilesExportRequest:
        """
        Create a participant profiles export request.

        Note: date_range parameter is ignored as participant profiles don't use date filtering.

        Args:
            participant: The Participant object (represents batch export)
            date_range: Dictionary with date range (ignored for this export type)

        Returns:
            ParticipantProfilesExportRequest object
        """
        profiles_config = self.get_config_section()
        participant_ids = profiles_config.get("participant_ids", [])

        # Check if we're exporting all participants
        if not participant_ids:
            # Export all - use null for participantIds
            request = ParticipantProfilesExportRequest(participantIds=None)
            self.logger.debug("Created export request for ALL participants")
        else:
            # Export specific participants
            # Convert integer IDs to strings per API contract
            if hasattr(participant, 'batch_participant_ids'):
                participant_ids = participant.batch_participant_ids

            participant_ids_str = [str(pid) for pid in participant_ids]

            request = ParticipantProfilesExportRequest(participantIds=participant_ids_str)

            self.logger.debug(
                f"Created export request for {len(participant_ids_str)} participants: "
                f"{participant_ids_str[:5]}{'...' if len(participant_ids_str) > 5 else ''}"
            )

        return request

    def request_export(
        self,
        participant: Participant,
        export_request: ParticipantProfilesExportRequest
    ) -> str:
        """
        Request participant profiles export via API.

        Args:
            participant: The Participant object (represents batch export)
            export_request: The ParticipantProfilesExportRequest object

        Returns:
            Export ID string

        Raises:
            VibrentHealthAPIError: If API call fails
        """
        export_id = self.client.request_participant_profiles_export(export_request)

        participant_count = len(export_request.participantIds) if export_request.participantIds else "all"
        self.logger.debug(
            f"Requested participant profiles export for {participant_count} participant(s): "
            f"export_id={export_id}"
        )

        return export_id

    def get_item_identifier(self, participant: Participant) -> str:
        """
        Get unique identifier for the batch export.

        Args:
            participant: The Participant object

        Returns:
            String identifier
        """
        profiles_config = self.get_config_section()
        participant_ids = profiles_config.get("participant_ids", [])

        if not participant_ids:
            return "all_participants"
        else:
            return f"batch_{len(participant_ids)}_participants"

    def get_item_display_name(self, participant: Participant) -> str:
        """
        Get human-readable display name for the batch export.

        Args:
            participant: The Participant object

        Returns:
            Formatted string describing the export
        """
        profiles_config = self.get_config_section()
        participant_ids = profiles_config.get("participant_ids", [])

        if not participant_ids:
            return "All Participants"
        else:
            return f"Batch Export ({len(participant_ids)} participants)"

    def get_output_directory_name(self) -> str:
        """
        Get the output directory name for participant profiles exports.

        Returns:
            Directory name (e.g., 'participant_profiles_exports')
        """
        output_config = self.config_manager.get_output_config()
        return output_config.get("participant_profiles_exports_dir", "participant_profiles_exports")
