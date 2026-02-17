#!/usr/bin/env python3
"""
Communication Events Exporter for Vibrent Health API Client

This module provides functionality to export communication events data
(email, SMS) from the Vibrent Health API with filtering capabilities.
"""

import logging
from typing import Dict, List, Optional

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import (
    CommunicationEventsExportRequest,
    CommunicationEventSource,
    CommunicationEventType,
    Participant
)


class CommunicationEventsExporter(BaseExporter):
    """
    Exporter for communication events data (email, SMS).

    This exporter handles batch export of communication events for participants with
    optional filtering by event sources, event types, and date range.

    Key Characteristics:
    - Batch export: One request can export events for multiple participants
    - Date range optional: Can export all events or filter by date
    - Event filtering: Filter by source (ITERABLE, SES, TWILIO) and type (EMAIL_*, SMS_*)
    - "Export all" behavior: Empty/null participantIds exports events for ALL participants
    - String IDs: Participant IDs must be strings per API contract

    Configuration Keys:
    - communication_events_export.participant_ids: List of participant IDs (integers in config, converted to strings)
    - communication_events_export.use_date_range: Whether to filter by date range
    - communication_events_export.date_range: Date range configuration
    - communication_events_export.event_sources: Filter by communication sources
    - communication_events_export.event_types: Filter by event types
    - communication_events_export.manifest_only: Whether to export only manifest metadata

    Example:
        >>> config_manager = ConfigManager()
        >>> client = VibrentHealthAPIClient(config_manager)
        >>> exporter = CommunicationEventsExporter(client, config_manager)
        >>> metadata = exporter.run()
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize Communication Events exporter.

        Args:
            client: Authenticated Vibrent Health API client
            config_manager: Configuration manager instance
        """
        super().__init__(client, config_manager)
        self.logger = logging.getLogger(__name__)

        # Load communication events specific configuration
        self.comm_events_config = self.config_manager.get("communication_events_export", {})

        # Get filtering parameters
        self.event_sources = self.comm_events_config.get("event_sources")
        self.event_types = self.comm_events_config.get("event_types")
        self.manifest_only = self.comm_events_config.get("manifest_only", False)

        # Validate event sources if provided
        if self.event_sources:
            invalid_sources = [
                source for source in self.event_sources
                if not CommunicationEventSource.is_valid(source)
            ]
            if invalid_sources:
                self.logger.warning(
                    f"Invalid event sources will be ignored: {invalid_sources}. "
                    f"Valid sources: {CommunicationEventSource.get_all_sources()}"
                )
                self.event_sources = [
                    source for source in self.event_sources
                    if CommunicationEventSource.is_valid(source)
                ]

        # Validate event types if provided
        if self.event_types:
            invalid_types = [
                event_type for event_type in self.event_types
                if not CommunicationEventType.is_valid(event_type)
            ]
            if invalid_types:
                self.logger.warning(
                    f"Invalid event types will be ignored: {invalid_types}. "
                    f"Valid types: {CommunicationEventType.get_all_types()}"
                )
                self.event_types = [
                    event_type for event_type in self.event_types
                    if CommunicationEventType.is_valid(event_type)
                ]

        # Log configuration
        self.logger.info("Communication Events Exporter initialized")
        if self.event_sources:
            self.logger.info(f"Event sources filter: {self.event_sources}")
        else:
            self.logger.info("Event sources filter: ALL sources")

        if self.event_types:
            self.logger.info(f"Event types filter: {self.event_types}")
        else:
            self.logger.info("Event types filter: ALL event types")

        self.logger.info(f"Manifest only: {self.manifest_only}")

    def get_export_type(self) -> str:
        """Get the export type identifier."""
        return "communication_events"

    def get_config_section(self):
        """Get the configuration section for this export type."""
        return self.config_manager.get("communication_events_export", {})

    def get_output_directory_name(self) -> str:
        """Get the output directory name for communication events exports."""
        output_config = self.config_manager.get_output_config()
        return output_config.get("communication_events_exports_dir", "communication_events_exports")

    def get_items(self) -> List[Participant]:
        """
        Get the list of participants to export.

        This is a BATCH export, so we return a single Participant object that represents
        the entire batch request, not individual participants.

        Returns:
            List with single Participant representing the batch export
        """
        comm_events_config = self.get_config_section()
        participant_ids = comm_events_config.get("participant_ids", [])

        # Create a single batch Participant object
        if not participant_ids:
            # Export all participants
            self.logger.info("Configuration set to export ALL participants")
            return [Participant(id=0, name="All Participants - Communication Events")]
        else:
            # Export specific participants - create single batch item
            self.logger.info(f"Configuration set to export events for {len(participant_ids)} specific participants")
            batch_participant = Participant(
                id=0,
                name=f"Batch Export ({len(participant_ids)} participants)"
            )
            # Store the IDs as a custom attribute (will be used in filter_items and create_export_request)
            batch_participant.batch_participant_ids = participant_ids
            return [batch_participant]

    def filter_items(self, items: List[Participant]) -> List[Participant]:
        """
        Apply configuration-based filtering to participants.

        For communication events, this validates:
        1. Maximum participants limit
        2. Exclusions (if specified)

        Args:
            items: List with single Participant representing batch export

        Returns:
            Filtered list (usually same single item, or empty if all excluded)
        """
        if not items:
            return []

        comm_events_config = self.get_config_section()
        batch_participant = items[0]

        # Get the original participant IDs from the batch participant
        participant_ids = getattr(batch_participant, 'batch_participant_ids', None)

        # If exporting all participants, no filtering needed
        if not participant_ids:
            self.logger.info("Exporting events for all participants - no filtering applied")
            return items

        # Apply exclusions
        exclude_ids = comm_events_config.get("exclude_participant_ids", [])
        if exclude_ids:
            original_count = len(participant_ids)
            participant_ids = [pid for pid in participant_ids if pid not in exclude_ids]
            excluded_count = original_count - len(participant_ids)
            if excluded_count > 0:
                self.logger.info(f"Excluded {excluded_count} participant(s) from export")

        # Apply max_participants limit
        max_participants = comm_events_config.get("max_participants")
        if max_participants and len(participant_ids) > max_participants:
            self.logger.info(f"Limiting to first {max_participants} participants (was {len(participant_ids)})")
            participant_ids = participant_ids[:max_participants]

        # If all participants were filtered out, return empty list
        if not participant_ids:
            self.logger.warning("All participants were filtered out - no exports will be created")
            return []

        # Update the batch participant with filtered IDs
        batch_participant.batch_participant_ids = participant_ids
        batch_participant.name = f"Batch Export ({len(participant_ids)} participants)"

        self.logger.info(f"After filtering: {len(participant_ids)} participant(s) will be exported")
        return [batch_participant]

    def create_export_request(
        self,
        item: Participant,
        date_range: Dict[str, int]
    ) -> CommunicationEventsExportRequest:
        """
        Create a communication events export request.

        Args:
            item: Participant object representing the batch
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            CommunicationEventsExportRequest object
        """
        # Get participant IDs from the batch participant object
        participant_ids_int = getattr(item, 'batch_participant_ids', None)

        # Convert to strings if we have IDs (API requires strings)
        if participant_ids_int:
            participant_ids_str = [str(pid) for pid in participant_ids_int]
        else:
            participant_ids_str = None

        # Extract date range values
        date_from = date_range.get('start_time') if date_range else None
        date_to = date_range.get('end_time') if date_range else None

        # Create the export request
        request = CommunicationEventsExportRequest(
            participantIds=participant_ids_str,
            dateFrom=date_from,
            dateTo=date_to,
            manifestOnly=self.manifest_only,
            eventSources=self.event_sources if self.event_sources else None,
            eventTypes=self.event_types if self.event_types else None
        )

        # Log request details
        if participant_ids_str:
            self.logger.debug(f"Batch export request for {len(participant_ids_str)} participant(s)")
        else:
            self.logger.debug("Batch export request for ALL participants")

        if date_from and date_to:
            self.logger.debug(f"Date range: {date_from} to {date_to}")
        else:
            self.logger.debug("No date range filter - using API defaults")

        if self.event_sources:
            self.logger.debug(f"Event sources: {self.event_sources}")
        if self.event_types:
            self.logger.debug(f"Event types: {self.event_types}")

        return request

    def request_export(self, item: Participant, export_request: CommunicationEventsExportRequest) -> str:
        """
        Request a communication events export.

        Args:
            item: Participant object (not used for batch export)
            export_request: The export request configuration

        Returns:
            Export ID string
        """
        return self.client.request_communication_events_export(export_request)

    def get_item_identifier(self, item: Participant) -> str:
        """
        Get a string identifier for the item.

        For batch exports, returns "batch" identifier.

        Args:
            item: Participant object

        Returns:
            String identifier
        """
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"batch_{len(participant_ids)}_participants"
        else:
            return "batch_all_participants"

    def get_item_display_name(self, item: Participant) -> str:
        """
        Get human-readable display name for the batch export.

        Args:
            item: Participant object

        Returns:
            Formatted string describing the export
        """
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"Communication Events - Batch Export ({len(participant_ids)} participants)"
        else:
            return "Communication Events - All Participants"
