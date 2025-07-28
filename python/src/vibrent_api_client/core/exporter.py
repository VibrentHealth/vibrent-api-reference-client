"""
Survey data exporter for Vibrent Health APIs
"""

import json
import logging
import os
import time
import zipfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from .client import VibrentHealthAPIClient
from .config import ConfigManager
from .constants import (
    ErrorMessages, SuccessMessages, TimeConstants, ExportStatus,
    FileConstants, ExportFormat
)
from ..models import ExportRequest, ExportMetadata


class SurveyDataExporter:
    """Main class for orchestrating the survey data export process"""

    @staticmethod
    def split_date_range_into_chunks(start_time: int, end_time: int, chunk_size_ms: int = TimeConstants.MS_PER_6_MONTHS) -> List[Dict[str, int]]:
        """
        Split a date range into chunks of specified size
        
        Args:
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            chunk_size_ms: Size of each chunk in milliseconds
            
        Returns:
            List of dictionaries with 'start_time' and 'end_time' for each chunk
        """
        chunks = []
        current_start = start_time

        while current_start < end_time:
            current_end = min(current_start + chunk_size_ms, end_time)
            chunks.append({
                'start_time': current_start,
                'end_time': current_end
            })
            current_start = current_end

        return chunks

    @staticmethod
    def merge_json_files(file_paths: List[Path], output_path: Path) -> bool:
        """
        Merge multiple JSON files into a single file
        
        Args:
            file_paths: List of JSON file paths to merge
            output_path: Path for the merged output file
            
        Returns:
            True if merge was successful, False otherwise
        """
        try:
            merged_data = []

            for file_path in file_paths:
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        # Handle both array and object formats
                        if isinstance(data, list):
                            merged_data.extend(data)
                        else:
                            merged_data.append(data)

            # Write merged data to output file
            with open(output_path, 'w') as f:
                json.dump(merged_data, f, indent=2)

            return True

        except Exception as e:
            logging.getLogger(__name__).error(f"Error merging JSON files: {str(e)}")
            return False

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
        self.extract_files = output_config.get("extract_files", True)
        self.remove_zip_after_extract = output_config.get("remove_zip_after_extract", True)

        # Get monitoring configuration
        monitoring_config = export_config.get("monitoring", {})
        self.polling_interval = monitoring_config.get("polling_interval", TimeConstants.DEFAULT_POLLING_INTERVAL)
        self.max_wait_time = monitoring_config.get("max_wait_time")
        self.continue_on_failure = monitoring_config.get("continue_on_failure", True)

        # Create output directory with timestamp (UTC)
        timestamp = datetime.now(timezone.utc).strftime("%d_%m_%Y_%H%M%S")
        
        # Get the survey output directory
        survey_output_dir = self.config_manager.get_survey_output_directory()
        self.output_dir = Path(survey_output_dir) / f"survey_data_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.export_session_id = f"export_{timestamp}"

        # Track start time for duration calculation (UTC)
        self.start_time = datetime.now(timezone.utc)

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

        # Initialize surveys list in metadata for tracking export details
        self.export_metadata.surveys = []

    def create_export_request(self, start_time: int = None, end_time: int = None) -> ExportRequest:
        """Create export request based on configuration or provided date range"""
        if start_time is None or end_time is None:
            date_range = self.config_manager.get_date_range()
            start_time = date_range["start_time"]
            end_time = date_range["end_time"]

        return ExportRequest(
            dateFrom=start_time,
            dateTo=end_time,
            format=self.export_format
        )

    def wait_for_exports_completion(self) -> Tuple[Dict[str, any], List[str]]:
        """Wait for all exports to complete and return completed and failed exports"""
        completed_exports = {}
        failed_exports = []
        
        # Flatten all export IDs from all surveys in metadata
        all_export_ids = []
        for survey in self.export_metadata.surveys:
            for export_detail in survey['export_details']:
                all_export_ids.append(export_detail['exportId'])
        
        pending_exports = set(all_export_ids)
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
                f"Status after this check: TOTAL: {len(all_export_ids)}, COMPLETED: {cumulative_status_counts['COMPLETED']}, FAILED: {cumulative_status_counts['FAILED']}, IN_PROGRESS: {cumulative_status_counts['IN_PROGRESS']}")

        return completed_exports, failed_exports

    def extract_export_files(self, export_metadata) -> None:
        """
        Extract export files (JSON or CSV) from zip archives based on configured format
        
        Args:
            export_metadata: ExportMetadata object containing all export information
        """
        if not self.extract_files:
            self.logger.info("File extraction disabled in configuration")
            return

        self.logger.info(f"Extracting {self.export_format} files from zip archives")

        # Track extracted filenames to handle conflicts
        extracted_filenames = {}

        # Process all surveys and their export details
        for survey in export_metadata.surveys:
            for export_detail in survey['export_details']:
                if not export_detail.get('file_path'):
                    continue
                
                zip_path = Path(export_detail['file_path'])
                if not zip_path.exists():
                    continue
                
                chunk_index = export_detail.get('chunk_index', 0)
                total_chunks = export_detail.get('total_chunks', 1)
                
                extraction_successful = True
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            original_filename = file_info.filename
                            
                            # Generate unique filename with postfix if needed
                            if total_chunks > 1:
                                # Add chunk postfix for multiple exports
                                name, ext = os.path.splitext(original_filename)
                                postfix_filename = f"{name}_part_{chunk_index + 1}{ext}"
                            else:
                                postfix_filename = original_filename
                            
                            # Check if filename already exists and add counter if needed
                            final_filename = postfix_filename
                            counter = 1
                            while final_filename in extracted_filenames:
                                name, ext = os.path.splitext(postfix_filename)
                                final_filename = f"{name}_{counter}{ext}"
                                counter += 1
                            
                            extracted_filenames[final_filename] = True
                            extracted_path = self.output_dir / final_filename
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
                    self.logger.error(f"Error extracting {zip_path}: {str(e)}")
                    extraction_successful = False

                if extraction_successful and self.remove_zip_after_extract:
                    try:
                        zip_path.unlink()
                        self.logger.debug(f"Removed zip file: {zip_path}")
                    except Exception as e:
                        self.logger.error(f"Error deleting zip file {zip_path}: {str(e)}")

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

            if not self.request_exports(filtered_surveys):
                return

            completed_exports, failed_export_ids = self.wait_for_exports_completion()
            downloaded_files = self.download_exports(completed_exports)

            if downloaded_files:
                self.extract_export_files(self.export_metadata)
                
                # Merge files for surveys with multiple exports (JSON format only) - AFTER extraction
                if self.export_format == ExportFormat.JSON:
                    self.merge_extracted_survey_files()

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
        else:
            self.logger.info(f"Total surveys data to be exported: {len(filtered_surveys)} surveys")

        return filtered_surveys

    def request_exports(self, filtered_surveys):
        """Request exports for filtered surveys, handling date range splitting if needed"""
        # Get the date range from configuration
        date_range = self.config_manager.get_date_range()
        start_time = date_range["start_time"]
        end_time = date_range["end_time"]

        # Check if date range is greater than 6 months
        date_range_duration = end_time - start_time
        needs_splitting = date_range_duration > TimeConstants.MS_PER_6_MONTHS

        if needs_splitting:
            self.logger.info(f"Date range ({date_range_duration / TimeConstants.MS_PER_DAY:.1f} days) exceeds 6 months. Splitting into chunks.")
            date_chunks = self.split_date_range_into_chunks(start_time, end_time)
            self.logger.info(f"Split date range into {len(date_chunks)} chunks")
        else:
            date_chunks = [{"start_time": start_time, "end_time": end_time}]

        for i, survey in enumerate(filtered_surveys):
            # Initialize survey in metadata with empty export details
            survey_dict = asdict(survey)
            survey_dict['export_details'] = []
            self.export_metadata.surveys.append(survey_dict)
            
            for j, chunk in enumerate(date_chunks):
                try:
                    chunk_start = chunk["start_time"]
                    chunk_end = chunk["end_time"]
                    
                    # Create export request for this chunk
                    export_request = self.create_export_request(chunk_start, chunk_end)
                    
                    if needs_splitting:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_surveys)}][{j + 1}/{len(date_chunks)}] Requesting export for survey id: {survey.platformFormId} "
                            f"(Name: '{survey.name}') - Date range: {datetime.fromtimestamp(chunk_start / 1000, tz=timezone.utc).strftime('%Y-%m-%d')} ({chunk_start}) to {datetime.fromtimestamp(chunk_end / 1000, tz=timezone.utc).strftime('%Y-%m-%d')}  ({chunk_end})")
                    else:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_surveys)}] Requesting export for survey id: {survey.platformFormId} (Name: '{survey.name}')")

                    export_id = self.client.request_survey_export(survey.platformFormId, export_request)
                    
                    # Create export detail with chunk information
                    export_detail = {
                        "exportId": export_id,
                        "chunk_start": chunk_start,
                        "chunk_end": chunk_end,
                        "chunk_index": j if needs_splitting else 0,
                        "total_chunks": len(date_chunks) if needs_splitting else 1,
                        "status": None,  # Will be updated during download
                        "file_path": None  # Will be updated during download
                    }
                    
                    # Add export detail to the survey in metadata
                    survey_dict['export_details'].append(export_detail)
                    
                    if needs_splitting:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_surveys)}][{j + 1}/{len(date_chunks)}] Requested export for survey id: {survey.platformFormId}, export id: {export_id}")
                    else:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_surveys)}] Requested export for survey id: {survey.platformFormId}, export id: {export_id}")
                    
                    time.sleep(0.5)

                except Exception as e:
                    self.logger.error(ErrorMessages.EXPORT_REQUEST_FAILED.format(
                        survey_id=survey.platformFormId, error=str(e)
                    ))
                    self.export_metadata.failures.append({
                        "surveyId": survey.platformFormId,
                        "error": str(e),
                        "stage": "export_request",
                        "chunk_index": j if needs_splitting else None
                    })

        # Check if any exports were successfully requested
        total_exports = sum(len(survey['export_details']) for survey in self.export_metadata.surveys)
        if total_exports == 0:
            self.logger.error("No exports were successfully requested")
            return False
        else:
            self.logger.info(f"Successfully requested {total_exports} exports")
            return True

    def download_exports(self, completed_exports):
        """Download completed exports and merge files if needed"""
        downloaded_files = []
        survey_files = {}  # Track files by survey ID for merging
        
        for i, (export_id, status) in enumerate(completed_exports.items(), start=1):
            try:
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloading export: {export_id}")
                file_path = self.client.download_export(export_id, self.output_dir)
                relative_path = os.path.relpath(file_path, start=os.getcwd())
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloaded: {relative_path}")
                downloaded_files.append(file_path)

                # Find and update the export detail in metadata
                for survey in self.export_metadata.surveys:
                    for export_detail in survey['export_details']:
                        if export_detail['exportId'] == export_id:
                            # Update the export detail with status and file path
                            export_detail['status'] = asdict(status)
                            export_detail['file_path'] = str(file_path)
                            
                            # Track files by survey for potential merging
                            survey_id = survey['platformFormId']
                            if survey_id not in survey_files:
                                survey_files[survey_id] = []
                            survey_files[survey_id].append(file_path)
                            break
                    else:
                        continue
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

    def merge_extracted_survey_files(self) -> None:
        """
        Merge extracted JSON files for each survey into a single file
        This method runs AFTER extraction, so it works with the actual JSON files
        """
        # Group extracted files by survey ID
        survey_files = {}
        
        for survey in self.export_metadata.surveys:
            survey_id = survey['platformFormId']
            extracted_files = []
            
            for export_detail in survey['export_details']:
                if export_detail.get('file_path'):
                    # Find the corresponding extracted JSON file
                    zip_path = Path(export_detail['file_path'])
                    chunk_index = export_detail.get('chunk_index', 0)
                    total_chunks = export_detail.get('total_chunks', 1)
                    
                    # Look for the extracted file in the survey_responses directory
                    survey_responses_dir = self.output_dir / "survey_responses"
                    if survey_responses_dir.exists():
                        # Find the extracted file with the correct postfix
                        for extracted_file in survey_responses_dir.glob(f"*_part_{chunk_index + 1}.json"):
                            if str(survey_id) in extracted_file.name:
                                extracted_files.append(extracted_file)
                                break
            
            if extracted_files:
                survey_files[survey_id] = extracted_files
        
        # Merge files for each survey
        for survey_id, files in survey_files.items():
            if len(files) > 1:
                self.logger.info(f"Merging {len(files)} extracted files for survey {survey_id}")
                
                # Create merged filename based on the first file's name pattern
                if files:
                    first_file = files[0]
                    # Extract the base name without the _part_X suffix
                    base_name = first_file.stem  # Remove .json extension
                    if "_part_" in base_name:
                        base_name = base_name.rsplit("_part_", 1)[0]  # Remove _part_X
                    
                    # Create merged filename with _merged suffix
                    merged_filename = f"{base_name}_merged.json"
                    merged_path = survey_responses_dir / merged_filename
                else:
                    # Fallback naming if no files found
                    merged_filename = f"survey_{survey_id}_merged.json"
                    merged_path = survey_responses_dir / merged_filename
                
                # Merge the files
                if self.merge_json_files(files, merged_path):
                    self.logger.info(f"Successfully merged extracted files for survey {survey_id} to: {merged_path}")
                    
                    # Update export details in metadata to include merged file info
                    for survey in self.export_metadata.surveys:
                        if survey['platformFormId'] == survey_id:
                            for export_detail in survey['export_details']:
                                export_detail["merged_file"] = str(merged_path)
                            break
                else:
                    self.logger.error(f"Failed to merge extracted files for survey {survey_id}")
            elif len(files) == 1:
                # Single file - no merging needed, but update export details
                for survey in self.export_metadata.surveys:
                    if survey['platformFormId'] == survey_id:
                        for export_detail in survey['export_details']:
                            export_detail["merged_file"] = str(files[0])
                        break

    def merge_survey_files(self, survey_files: Dict[int, List[Path]]) -> None:
        """
        Merge multiple files for each survey into a single file
        
        Args:
            survey_files: Dictionary mapping survey_id to list of file paths
        """
        for survey_id, files in survey_files.items():
            if len(files) > 1:
                self.logger.info(f"Merging {len(files)} files for survey {survey_id}")
                
                # Create merged filename
                merged_filename = f"survey_{survey_id}_merged.json"
                merged_path = self.output_dir / merged_filename
                
                # Merge the files
                if self.merge_json_files(files, merged_path):
                    self.logger.info(f"Successfully merged files for survey {survey_id} to: {merged_path}")
                    
                    # Update export details in metadata to include merged file info
                    for survey in self.export_metadata.surveys:
                        if survey['platformFormId'] == survey_id:
                            for export_detail in survey['export_details']:
                                export_detail["merged_file"] = str(merged_path)
                            break
                else:
                    self.logger.error(f"Failed to merge files for survey {survey_id}")
            elif len(files) == 1:
                # Single file - no merging needed, but update export details
                for survey in self.export_metadata.surveys:
                    if survey['platformFormId'] == survey_id:
                        for export_detail in survey['export_details']:
                            export_detail["merged_file"] = str(files[0])
                        break

    def update_metadata(self, completed_exports, failed_export_ids, filtered_surveys):
        """Update export metadata"""
        self.export_metadata.successful_exports = len(completed_exports)
        self.export_metadata.failed_exports = len(failed_export_ids) + len(self.export_metadata.failures)

        # Check metadata configuration
        metadata_config = self.config_manager.get_metadata_config()
        include_survey_details = metadata_config.get("include_survey_details", True)
        include_export_status = metadata_config.get("include_export_status", True)

        # If survey details are disabled, clear the surveys list
        if not include_survey_details:
            self.export_metadata.surveys = []
        elif not include_export_status:
            # Keep surveys but clear export details
            for survey in self.export_metadata.surveys:
                survey['export_details'] = []

        end_time = datetime.now(timezone.utc)
        self.export_metadata.end_timestamp = end_time.isoformat()
        self.export_metadata.duration_seconds = (end_time - self.start_time).total_seconds()

    def log_export_summary(self):
        """Log summary of the export process"""
        self.logger.info(SuccessMessages.EXPORT_COMPLETED)
        self.logger.info(f"Total surveys: {self.export_metadata.total_surveys}")
        self.logger.info(f"Successful exports: {self.export_metadata.successful_exports}")
        self.logger.info(f"Failed exports: {len(self.export_metadata.failures)}")

        # Show details about multiple exports per survey
        total_export_requests = sum(len(survey.get('export_details', [])) for survey in self.export_metadata.surveys)
        if total_export_requests > self.export_metadata.total_surveys:
            self.logger.info(f"Total export requests: {total_export_requests} (multiple exports per survey due to date range splitting)")
        
        self.logger.info(f"Duration: {self.export_metadata.duration_seconds:.2f} seconds")
        self.logger.info(f"Output directory: {self.output_dir}")
