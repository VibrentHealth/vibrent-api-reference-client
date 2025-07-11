"""
Survey data exporter for Vibrent Health APIs
"""

import json
import logging
import os
import time
import zipfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from .client import VibrentHealthAPIClient
from .config import ConfigManager
from .constants import (
    ErrorMessages, SuccessMessages, TimeConstants, ExportStatus,
    FileConstants
)
from ..models import ExportRequest, ExportMetadata


class SurveyDataExporter:
    """Main class for orchestrating the survey data export process"""

    def __init__(self, config_manager: ConfigManager, environment: str = None, output_base_dir: str = None):
        self.config_manager = config_manager
        self.environment = environment or config_manager.get("environment.default")
        self.client = VibrentHealthAPIClient(config_manager, self.environment)
        self.logger = logging.getLogger(__name__)

        # Get output configuration
        output_config = self.config_manager.get_output_config()
        self.output_base_dir = Path(output_base_dir or output_config.get("base_directory", "survey_exports"))

        # Get export configuration
        export_config = self.config_manager.get("export")
        self.export_format = export_config.get("format", "JSON")
        self.extract_json = output_config.get("extract_json", True)
        self.remove_zip_after_extract = output_config.get("remove_zip_after_extract", True)

        # Get monitoring configuration
        monitoring_config = export_config.get("monitoring", {})
        self.polling_interval = monitoring_config.get("polling_interval", TimeConstants.DEFAULT_POLLING_INTERVAL)
        self.max_wait_time = monitoring_config.get("max_wait_time")
        self.continue_on_failure = monitoring_config.get("continue_on_failure", True)

        # Create output directory with timestamp
        timestamp = datetime.now().strftime("%d_%m_%Y_%H%M%S")
        
        # Get the survey output directory
        survey_output_dir = self.config_manager.get_survey_output_directory()
        self.output_dir = Path(survey_output_dir) / f"survey_data_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.export_session_id = f"export_{timestamp}"

        # Track start time for duration calculation
        self.start_time = datetime.now()

        self.export_metadata = ExportMetadata(
            export_session_id=self.export_session_id,
            start_timestamp=self.start_time.isoformat(),
            total_surveys=0,
            successful_exports=0,
            failed_exports=0,
            output_directory=str(self.output_dir),
            surveys=[],
            failures=[]
        )

        # Track export details by survey ID for embedding in survey objects
        self.export_details_by_survey = {}

    def create_export_request(self) -> ExportRequest:
        """Create export request based on configuration"""
        date_range = self.config_manager.get_date_range()

        return ExportRequest(
            dateFrom=date_range["start_time"],
            dateTo=date_range["end_time"],
            format=self.export_format
        )

    def wait_for_exports_completion(self, export_mapping: Dict[int, str]) -> Tuple[Dict[str, any], List[str]]:
        """Wait for all exports to complete and return completed and failed exports"""
        completed_exports = {}
        failed_exports = []
        pending_exports = set(export_mapping.values())
        start_wait_time = time.time()

        # Initialize cumulative status counts
        cumulative_status_counts = {"COMPLETED": 0, "FAILED": 0, "IN_PROGRESS": len(pending_exports)}

        self.logger.info(f"Checking Export Status: Waiting for {len(pending_exports)} exports to complete")

        while pending_exports:
            # Check if we've exceeded max wait time
            if self.max_wait_time and (time.time() - start_wait_time) > self.max_wait_time:
                self.logger.warning(f"Maximum wait time ({self.max_wait_time}s) exceeded. {len(pending_exports)} exports still pending.")
                break

            time.sleep(self.polling_interval)

            # Reset current iteration status counts
            current_status_counts = {"COMPLETED": 0, "FAILED": 0, "IN_PROGRESS": 0}

            for export_id in list(pending_exports):
                try:
                    status = self.client.get_export_status(export_id)

                    if status.status == ExportStatus.COMPLETED:
                        current_status_counts["COMPLETED"] += 1
                        completed_exports[export_id] = status
                        pending_exports.remove(export_id)

                    elif status.status == ExportStatus.FAILED:
                        current_status_counts["FAILED"] += 1
                        failed_exports.append(export_id)
                        pending_exports.remove(export_id)

                        # Add to failures metadata
                        self.export_metadata.failures.append({
                            "exportId": export_id,
                            "failureReason": status.failureReason,
                            "status": asdict(status)
                        })

                    elif status.status in [ExportStatus.SUBMITTED, ExportStatus.IN_PROGRESS]:
                        current_status_counts["IN_PROGRESS"] += 1

                except Exception as e:
                    self.logger.error(f"Error checking status for {export_id}: {str(e)}")
                    if not self.continue_on_failure:
                        raise
                    current_status_counts["FAILED"] += 1
                    failed_exports.append(export_id)
                    pending_exports.remove(export_id)

            # Update cumulative status counts
            cumulative_status_counts["COMPLETED"] += current_status_counts["COMPLETED"]
            cumulative_status_counts["FAILED"] += current_status_counts["FAILED"]
            cumulative_status_counts["IN_PROGRESS"] = len(pending_exports)

            self.logger.info(
                f"Status after this check: TOTAL: {len(export_mapping)}, COMPLETED: {cumulative_status_counts['COMPLETED']}, FAILED: {cumulative_status_counts['FAILED']}, IN_PROGRESS: {cumulative_status_counts['IN_PROGRESS']}")

        return completed_exports, failed_exports

    def extract_json_files(self, zip_files: List[Path]) -> None:
        """Extract JSON files from zip archives"""
        if zip_files is None:
            self.logger.error("List of zip files is null")
            return

        if not self.extract_json:
            self.logger.info("JSON extraction disabled in configuration")
            return

        self.logger.info("Extracting JSON files from zip archives")

        for zip_file in zip_files:
            extraction_successful = True
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.endswith(FileConstants.JSON_EXTENSION):
                            extracted_path = self.output_dir / file_info.filename
                            extracted_path.parent.mkdir(parents=True, exist_ok=True)

                            with zip_ref.open(file_info) as source, open(extracted_path, 'wb') as target:
                                buffer = source.read(8192)
                                while buffer:
                                    target.write(buffer)
                                    buffer = source.read(8192)

                            # Show path relative to current working directory for cleaner logging
                            relative_path = os.path.relpath(extracted_path, start=os.getcwd())
                            self.logger.info(f"Extracted: {relative_path}")

            except Exception as e:
                self.logger.error(f"Error extracting {zip_file}: {str(e)}")
                extraction_successful = False

            if extraction_successful and self.remove_zip_after_extract:
                try:
                    zip_file.unlink()
                    self.logger.debug(f"Removed zip file: {zip_file}")
                except Exception as e:
                    self.logger.error(f"Error deleting zip file {zip_file}: {str(e)}")

    def save_export_metadata(self) -> None:
        """Save export metadata to JSON file"""
        metadata_config = self.config_manager.get_metadata_config()

        if not metadata_config.get("save_metadata", True):
            self.logger.info("Metadata saving disabled in configuration")
            return

        metadata_filename = metadata_config.get("filename", FileConstants.DEFAULT_METADATA_FILENAME)
        metadata_file = self.output_dir / metadata_filename

        try:
            with open(metadata_file, 'w') as f:
                json.dump(asdict(self.export_metadata), f, indent=2)

            # Show path relative to current working directory for cleaner logging
            relative_path = os.path.relpath(metadata_file, start=os.getcwd())
            self.logger.info(SuccessMessages.METADATA_SAVED.format(file_path=relative_path))
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {str(e)}")

    def run_export(self) -> None:
        """Run the complete export process"""
        try:
            self.logger.info(f"Starting survey data export (Session: {self.export_session_id})")
            surveys = self.get_surveys()
            if not surveys:
                return

            filtered_surveys = self.filter_surveys(surveys)
            if not filtered_surveys:
                return

            export_mapping = self.request_exports(filtered_surveys)
            if not export_mapping:
                return

            completed_exports, failed_export_ids = self.wait_for_exports_completion(export_mapping)
            downloaded_files = self.download_exports(completed_exports, export_mapping)

            if downloaded_files:
                self.extract_json_files(downloaded_files)

            self.update_metadata(completed_exports, failed_export_ids, filtered_surveys)
            self.save_export_metadata()
            self.log_export_summary()
        except Exception as e:
            self.logger.error(f"Export process failed: {str(e)}")
            raise

    def get_surveys(self):
        """Retrieve surveys and update metadata"""
        surveys = self.client.get_surveys()
        self.export_metadata.total_surveys = len(surveys)
        if not surveys:
            self.logger.warning(ErrorMessages.NO_SURVEYS_FOUND)
        return surveys

    def filter_surveys(self, surveys):
        """Filter surveys based on configuration"""
        survey_filter = self.config_manager.get_survey_filter()
        max_surveys = survey_filter.get("max_surveys")

        filtered_surveys = []
        for survey in surveys:
            if self.config_manager.should_include_survey(survey.platformFormId, survey.name):
                filtered_surveys.append(survey)
                if max_surveys and len(filtered_surveys) >= max_surveys:
                    break

        if not filtered_surveys:
            self.logger.warning("No surveys match the filter criteria")
        return filtered_surveys

    def request_exports(self, filtered_surveys):
        """Request exports for filtered surveys"""
        export_request = self.create_export_request()
        export_mapping = {}

        for i, survey in enumerate(filtered_surveys):
            try:
                self.logger.info(
                    f"[{i + 1}/{len(filtered_surveys)}] Requesting export for survey id: {survey.platformFormId} (Name: '{survey.name}')")
                export_id = self.client.request_survey_export(survey.platformFormId, export_request)
                self.logger.info(f"Export requested: {export_id}")
                export_mapping[survey.platformFormId] = export_id
                time.sleep(0.5)

            except Exception as e:
                self.logger.error(ErrorMessages.EXPORT_REQUEST_FAILED.format(
                    survey_id=survey.platformFormId, error=str(e)
                ))
                self.export_metadata.failures.append({
                    "surveyId": survey.platformFormId,
                    "error": str(e),
                    "stage": "export_request"
                })

        if not export_mapping:
            self.logger.error("No exports were successfully requested")
        return export_mapping

    def download_exports(self, completed_exports, export_mapping):
        """Download completed exports"""
        downloaded_files = []
        for i, (export_id, status) in enumerate(completed_exports.items(), start=1):
            try:
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloading export: {export_id}")
                file_path = self.client.download_export(export_id, self.output_dir)
                relative_path = os.path.relpath(file_path, start=os.getcwd())
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloaded: {relative_path}")
                downloaded_files.append(file_path)

                export_detail = {
                    "exportId": export_id,
                    "status": asdict(status),
                }

                for survey_id, exp_id in export_mapping.items():
                    if exp_id == export_id:
                        self.export_details_by_survey[survey_id] = export_detail
                        break

            except Exception as e:
                self.logger.error(ErrorMessages.EXPORT_DOWNLOAD_FAILED.format(
                    export_id=export_id, error=str(e)
                ))
                self.export_metadata.failures.append({
                    "exportId": export_id,
                    "error": str(e),
                    "stage": "download"
                })
        return downloaded_files

    def update_metadata(self, completed_exports, failed_export_ids, filtered_surveys):
        """Update export metadata"""
        self.export_metadata.successful_exports = len(completed_exports)
        self.export_metadata.failed_exports = len(failed_export_ids) + len(self.export_metadata.failures)

        metadata_config = self.config_manager.get_metadata_config()
        include_survey_details = metadata_config.get("include_survey_details", True)
        include_export_status = metadata_config.get("include_export_status", True)

        if include_survey_details:
            survey_dicts = []
            for survey in filtered_surveys:
                survey_dict = asdict(survey)
                if include_export_status and survey.platformFormId in self.export_details_by_survey:
                    survey_dict['export_details'] = self.export_details_by_survey[survey.platformFormId]
                survey_dicts.append(survey_dict)

            self.export_metadata.surveys = survey_dicts

        end_time = datetime.now()
        self.export_metadata.end_timestamp = end_time.isoformat()
        self.export_metadata.duration_seconds = (end_time - self.start_time).total_seconds()

    def log_export_summary(self):
        """Log summary of the export process"""
        self.logger.info(SuccessMessages.EXPORT_COMPLETED)
        self.logger.info(f"Total surveys: {self.export_metadata.total_surveys}")
        self.logger.info(f"Successful exports: {self.export_metadata.successful_exports}")
        self.logger.info(f"Failed exports: {self.export_metadata.failed_exports}")
        self.logger.info(f"Duration: {self.export_metadata.duration_seconds:.2f} seconds")
        self.logger.info(f"Output directory: {self.output_dir}")
