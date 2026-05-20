"""
EHR exporter for Vibrent Health API Client

This module contains the EHRExporter class which handles Electronic Health Record
(EHR) data export using the multi-participant batch endpoint to launch a single
Dagster job for all participants.
"""

from typing import Dict, List

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Participant, EHRMultiExportRequest


class EHRExporter(BaseExporter):
    """
    Exporter for Electronic Health Record (EHR) data.

    Uses the multi-participant endpoint (POST /api/ext/export/ehr/request) to export
    all configured participants in a single API call, launching one Dagster job.

    Configuration (in vibrent_config.yaml):
        ehr_export:
          participant_ids: [12345, 67890]
          max_participants: null
          exclude_participant_ids: null
          manifest_only: false
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        super().__init__(client, config_manager)
        self.logger.info("Initialized EHRExporter")

    def get_export_type(self) -> str:
        return "ehr"

    def get_items(self) -> List[Participant]:
        """
        Get a single batch item representing all participants.

        Returns a single Participant object that carries all participant IDs,
        so the orchestrator makes one API call instead of N.
        """
        self.logger.info("Loading participant list from configuration")
        ehr_config = self.get_config_section()
        participant_ids = ehr_config.get("participant_ids", [])

        if not participant_ids:
            error_msg = (
                "No participant IDs configured for EHR export. "
                "Please specify participant_ids in ehr_export configuration."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        batch_participant = Participant(
            id=0,
            name=f"Batch Export ({len(participant_ids)} participants)"
        )
        batch_participant.batch_participant_ids = participant_ids

        self.logger.info(f"Loaded {len(participant_ids)} participants for EHR batch export")
        return [batch_participant]

    def filter_items(self, items: List[Participant]) -> List[Participant]:
        """
        Apply exclusion and max_participants filtering within the batch.
        """
        if not items:
            return []

        ehr_config = self.get_config_section()
        batch_participant = items[0]
        participant_ids = getattr(batch_participant, 'batch_participant_ids', None)

        if not participant_ids:
            return items

        exclude_ids = ehr_config.get("exclude_participant_ids", [])
        if exclude_ids:
            original_count = len(participant_ids)
            participant_ids = [pid for pid in participant_ids if pid not in exclude_ids]
            excluded_count = original_count - len(participant_ids)
            if excluded_count > 0:
                self.logger.info(f"Excluded {excluded_count} participant(s) from export")

        max_participants = ehr_config.get("max_participants")
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

    def create_export_request(
        self,
        item: Participant,
        date_range: Dict[str, int]
    ) -> EHRMultiExportRequest:
        """
        Create a multi-participant EHR export request.
        """
        ehr_config = self.get_config_section()
        participant_ids = getattr(item, 'batch_participant_ids', None)
        manifest_only = ehr_config.get("manifest_only", False)

        date_from = date_range.get('start_time')
        date_to = date_range.get('end_time')

        request = EHRMultiExportRequest(
            dateFrom=date_from,
            dateTo=date_to,
            participantIds=participant_ids,
            manifestOnly=manifest_only
        )

        self.logger.debug(
            f"Created EHR batch export request: "
            f"{len(participant_ids) if participant_ids else 'all'} participants, "
            f"dateFrom={date_from}, dateTo={date_to}, manifestOnly={manifest_only}"
        )

        return request

    def request_export(self, item: Participant, export_request: EHRMultiExportRequest) -> str:
        """
        Request EHR data export via the multi-participant endpoint.
        Launches a single Dagster job for all participants.
        """
        return self.client.request_multi_ehr_export(export_request)

    def get_item_identifier(self, item: Participant) -> str:
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"batch_{len(participant_ids)}_participants"
        return "batch_all_participants"

    def get_item_display_name(self, item: Participant) -> str:
        participant_ids = getattr(item, 'batch_participant_ids', None)
        if participant_ids:
            return f"EHR - Batch Export ({len(participant_ids)} participants)"
        return "EHR - All Participants"

    def get_output_directory_name(self) -> str:
        output_config = self.config_manager.get_output_config()
        return output_config.get("ehr_exports_dir", "ehr_exports")
