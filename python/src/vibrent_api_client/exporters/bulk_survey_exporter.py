"""
Bulk survey exporter for Vibrent Health API Client

Exports multiple (or all) surveys in a single API call using the bulk
survey endpoint (/api/ext/export/survey/request).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.base_exporter import BaseExporter
from ..core.client import VibrentHealthAPIClient
from ..core.config import ConfigManager
from ..models import Survey, BulkSurveyExportRequest


@dataclass
class BulkSurveyItem:
    """Virtual item representing a bulk survey export batch."""
    survey_ids: List[int]
    all_surveys: bool
    id: int = 0
    name: str = "bulk_survey_export"
    displayName: str = "Bulk Survey Export"
    platformFormId: int = 0


class BulkSurveyExporter(BaseExporter):
    """
    Exporter for bulk survey data using the bulk export endpoint.

    Unlike SurveyExporter which calls /survey/{id}/request per form,
    this exporter sends a single request to /survey/request with all
    survey IDs (or allSurveys=true).

    Configuration (in vibrent_config.yaml):
        bulk_survey_export:
          use_date_range: true
          date_range:
            default_days_back: 30
          format: "JSON"
          remove_pii: false
          include_labels: false
          request:
            all_surveys: true
            survey_ids: null
            exclude_survey_ids: null
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        super().__init__(client, config_manager)
        self._date_from: Optional[int] = None
        self._date_to: Optional[int] = None
        self.logger.info("Initialized BulkSurveyExporter")

    def set_date_filter(self, date_from: int, date_to: int) -> None:
        self._date_from = date_from
        self._date_to = date_to

    def get_export_type(self) -> str:
        return "bulk_survey"

    def get_items(self) -> List[BulkSurveyItem]:
        self.logger.info("Building bulk survey export item from configuration")

        config = self.get_config_section()
        request_config = config.get("request", {})
        all_surveys = request_config.get("all_surveys", True)
        survey_ids = request_config.get("survey_ids")
        exclude_survey_ids = request_config.get("exclude_survey_ids")

        if all_surveys and not exclude_survey_ids:
            self.logger.info("Bulk export mode: all surveys")
            return [BulkSurveyItem(survey_ids=[], all_surveys=True,
                                   displayName="Bulk Survey Export (All Surveys)")]

        surveys = self.client.get_surveys(date_from=self._date_from, date_to=self._date_to)
        self.logger.info(f"Retrieved {len(surveys)} surveys from API")

        filtered_ids = []
        for survey in surveys:
            if not all_surveys and survey_ids is not None and survey.platformFormId not in survey_ids:
                continue
            if exclude_survey_ids and survey.platformFormId in exclude_survey_ids:
                continue
            filtered_ids.append(survey.platformFormId)

        if all_surveys and exclude_survey_ids:
            self.logger.info(f"Excluded {len(exclude_survey_ids)} survey(s) from all-surveys export")

        self.logger.info(f"Filtered to {len(filtered_ids)} survey IDs for bulk export")
        return [BulkSurveyItem(
            survey_ids=filtered_ids,
            all_surveys=False,
            displayName=f"Bulk Survey Export ({len(filtered_ids)} surveys)",
        )]

    def filter_items(self, items: List[BulkSurveyItem]) -> List[BulkSurveyItem]:
        return items

    def create_export_request(self, item: BulkSurveyItem, date_range: Dict[str, int]) -> BulkSurveyExportRequest:
        config = self.get_config_section()
        export_format = config.get("format", "JSON")
        remove_pii = config.get("remove_pii", False)
        include_labels = config.get("include_labels", False)

        request = BulkSurveyExportRequest(
            dateFrom=date_range["start_time"],
            dateTo=date_range["end_time"],
            format=export_format,
            removePII=remove_pii,
            includeLabels=include_labels,
            allSurveys=item.all_surveys,
            surveyIds=item.survey_ids if not item.all_surveys else None,
        )

        self.logger.debug(
            f"Created bulk survey export request: allSurveys={item.all_surveys}, "
            f"surveyIds={len(item.survey_ids)} IDs, format={export_format}"
        )
        return request

    def request_export(self, item: BulkSurveyItem, export_request: BulkSurveyExportRequest) -> str:
        export_id = self.client.request_bulk_survey_export(export_request)
        self.logger.debug(f"Requested bulk survey export: export_id={export_id}")
        return export_id

    def get_item_identifier(self, item: BulkSurveyItem) -> str:
        return "bulk_all" if item.all_surveys else f"bulk_{len(item.survey_ids)}"

    def get_item_display_name(self, item: BulkSurveyItem) -> str:
        return item.displayName

    def get_output_directory_name(self) -> str:
        output_config = self.config_manager.get_output_config()
        return output_config.get("bulk_survey_exports_dir", "bulk_survey_exports")
