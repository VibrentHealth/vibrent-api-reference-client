"""
Device exporter for Vibrent Health API Client

This module contains the DeviceExporter class which handles device data
export using the multi-participant batch endpoint to launch a single
Dagster job for all participants.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Participant, DeviceDataExportRequest, DeviceType, DeviceDataType


class DeviceExporter(BaseExporter):
    """
    Exporter for device data (Fitbit, Garmin, Apple HealthKit).

    Uses the multi-participant endpoint (POST /api/ext/export/device/request) to export
    all configured participants in a single API call, launching one Dagster job.

    Configuration (in vibrent_config.yaml):
        device_export:
          participant_ids: [12345, 67890]
          max_participants: null
          exclude_participant_ids: null
          device_types: ["FITBIT", "GARMIN"]
          data_types: ["SLEEP", "HEART_RATE"]
          manifest_only: false
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        super().__init__(client, config_manager)
        self.logger.info("Initialized DeviceExporter")

    def get_export_type(self) -> str:
        return "device"

    def get_items(self) -> List[Participant]:
        """
        Get a single batch item representing all participants.

        Returns a single Participant object that carries all participant IDs,
        so the orchestrator makes one API call instead of N.
        """
        self.logger.info("Loading participant list from configuration")
        device_config = self.get_config_section()
        participant_ids = device_config.get("participant_ids", [])

        if not participant_ids:
            error_msg = (
                "No participant IDs configured for device data export. "
                "Please specify participant_ids in device_export configuration."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        batch_participant = Participant(
            id=0,
            name=f"Batch Export ({len(participant_ids)} participants)"
        )
        batch_participant.batch_participant_ids = participant_ids

        self.logger.info(f"Loaded {len(participant_ids)} participants for device batch export")
        return [batch_participant]

    def filter_items(self, items: List[Participant]) -> List[Participant]:
        """
        Apply exclusion and max_participants filtering within the batch.
        """
        if not items:
            return []

        device_config = self.get_config_section()
        batch_participant = items[0]
        participant_ids = getattr(batch_participant, 'batch_participant_ids', None)

        if not participant_ids:
            return items

        exclude_ids = device_config.get("exclude_participant_ids", [])
        if exclude_ids:
            original_count = len(participant_ids)
            participant_ids = [pid for pid in participant_ids if pid not in exclude_ids]
            excluded_count = original_count - len(participant_ids)
            if excluded_count > 0:
                self.logger.info(f"Excluded {excluded_count} participant(s) from export")

        max_participants = device_config.get("max_participants")
        if max_participants and len(participant_ids) > max_participants:
            self.logger.info(f"Limiting to first {max_participants} participants (was {len(participant_ids)})")
            participant_ids = participant_ids[:max_participants]

        if not participant_ids:
            self.logger.warning("All participants were filtered out - no exports will be created")
            return []

        batch_participant.batch_participant_ids = participant_ids
        batch_participant.name = f"Batch Export ({len(participant_ids)} participants)"

        self.logger.info(f"After filtering: {len(participant_ids)} participant(s) will be exported")
        return [batch_participant]

    def create_export_request(self, item: Participant, date_range: Dict[str, int]) -> DeviceDataExportRequest:
        """
        Create a device data export request.

        Always uses multi-participant endpoint since both single and multi
        have the same 24h data mode limit, but multi supports 360-day manifest mode.
        """
        device_config = self.get_config_section()
        participant_ids = getattr(item, 'batch_participant_ids', None)
        manifest_only = device_config.get("manifest_only", False)

        device_types = device_config.get("device_types")
        data_types = device_config.get("data_types")

        if device_types is not None and len(device_types) == 0:
            device_types = None
        if data_types is not None and len(data_types) == 0:
            data_types = None

        if device_types:
            invalid_types = [dt for dt in device_types if not DeviceType.is_valid(dt)]
            if invalid_types:
                self.logger.warning(
                    f"Invalid device types: {invalid_types}. "
                    f"Valid types: {DeviceType.get_all_types()}"
                )

        if data_types:
            invalid_types = [dt for dt in data_types if not DeviceDataType.is_valid(dt)]
            if invalid_types:
                self.logger.warning(
                    f"Invalid data types: {invalid_types}. "
                    f"Valid types: {DeviceDataType.get_all_types()}"
                )

        date_from = date_range.get('start_time')
        date_to = date_range.get('end_time')

        request = DeviceDataExportRequest(
            dateFrom=date_from,
            dateTo=date_to,
            participantIds=participant_ids,
            deviceTypes=device_types,
            dataTypes=data_types,
            manifestOnly=manifest_only
        )

        self.logger.debug(
            f"Created device batch export request: "
            f"{len(participant_ids) if participant_ids else 'all'} participants, "
            f"dateFrom={date_from}, dateTo={date_to}, manifestOnly={manifest_only}"
        )

        return request

    def request_export(self, item: Participant, export_request: DeviceDataExportRequest) -> str:
        """
        Always uses multi-participant endpoint /device/request.
        Both single and multi have 24h data mode limit, but multi supports 360-day manifest.
        """
        return self.client.request_multi_device_export(export_request)

    def get_item_identifier(self, item: Participant) -> str:
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"batch_{len(participant_ids)}_participants"
        return "batch_all_participants"

    def get_item_display_name(self, item: Participant) -> str:
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"Device - Batch Export ({len(participant_ids)} participants)"
        return "Device - All Participants"

    def get_output_directory_name(self) -> str:
        output_config = self.config_manager.get_output_config()
        return output_config.get("device_exports_dir", "device_exports")
