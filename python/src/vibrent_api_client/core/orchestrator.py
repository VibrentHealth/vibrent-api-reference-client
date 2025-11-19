"""
Export orchestrator for Vibrent Health API Client

This module contains the ExportOrchestrator class which coordinates the complete
export workflow for any export type. It handles common operations like requesting
exports, polling for completion, downloading files, and managing metadata.
"""

import json
import logging
import os
import time
import zipfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .base_exporter import BaseExporter
from .config import ConfigManager
from .constants import ErrorMessages, ExportStatus, FileConstants, SuccessMessages, TimeConstants
from ..models import ExportMetadata


class ExportOrchestrator:
    """
    Orchestrates the complete export workflow for any export type.

    This class handles all common export operations:
    - Requesting exports with date range chunking
    - Polling for export completion
    - Downloading completed exports
    - Extracting files from ZIP archives
    - Merging multi-part exports
    - Tracking metadata

    The exporter-specific logic is delegated to the BaseExporter implementation.

    Usage:
        exporter = SurveyExporter(client, config_manager)
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

    Attributes:
        exporter: The export-specific implementation
        config_manager: Configuration manager
        client: API client (from exporter)
        output_dir: Output directory path
        export_metadata: Metadata tracking object
    """

    def __init__(self,
                 exporter: BaseExporter,
                 config_manager: ConfigManager,
                 output_base_dir: Optional[str] = None):
        """
        Initialize the export orchestrator.

        Args:
            exporter: Export-specific implementation (e.g., SurveyExporter)
            config_manager: Configuration manager instance
            output_base_dir: Optional base directory override
        """
        self.exporter = exporter
        self.config_manager = config_manager
        self.client = exporter.client
        self.logger = logging.getLogger(__name__)

        # Get output configuration
        output_config = self.config_manager.get_output_config()
        base_dir = output_base_dir or output_config.get("base_directory", FileConstants.OUTPUT_BASE_DIR)

        # Get export format
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

        # Get the export-specific output directory
        export_type = exporter.get_export_type()
        export_output_dir = exporter.get_output_directory_name()

        # Get the repo root for path construction
        self.output_dir = self._construct_output_path(base_dir, export_output_dir, timestamp)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.export_session_id = f"export_{export_type}_{timestamp}"

        # Track start time for duration calculation (UTC)
        self.start_time = datetime.now(timezone.utc)

        # Initialize metadata
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

        self.logger.info(f"Initialized ExportOrchestrator for {export_type} exports")
        self.logger.info(f"Output directory: {self.output_dir}")

    def _construct_output_path(self, base_dir: str, export_dir: str, timestamp: str) -> Path:
        """
        Construct the full output path.

        Args:
            base_dir: Base output directory (e.g., 'output')
            export_dir: Export-specific directory (e.g., 'survey_exports')
            timestamp: Timestamp string for uniqueness

        Returns:
            Path object for the output directory
        """
        # Get the repo root
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)

        # Navigate up to find repo root
        repo_root = current_dir
        while repo_root != os.path.dirname(repo_root):
            if (os.path.exists(os.path.join(repo_root, "python")) and
                os.path.exists(os.path.join(repo_root, "shared"))):
                break
            repo_root = os.path.dirname(repo_root)

        # Construct path: repo_root/python/output/survey_exports/survey_data_timestamp
        full_base_dir = os.path.join(repo_root, "python", base_dir)
        export_type = self.exporter.get_export_type()
        session_name = f"{export_type}_data_{timestamp}"

        return Path(full_base_dir) / export_dir / session_name

    @staticmethod
    def split_date_range_into_chunks(start_time: int, end_time: int,
                                     chunk_size_ms: int = TimeConstants.MS_PER_6_MONTHS) -> List[Dict[str, int]]:
        """
        Split a date range into chunks of specified size.

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

    def run_export(self) -> ExportMetadata:
        """
        Execute the complete export workflow.

        This is the main entry point that coordinates all export operations.

        Returns:
            ExportMetadata object with export results

        Raises:
            Exception: If export process fails and continue_on_failure is False
        """
        try:
            export_type = self.exporter.get_export_type()
            self.logger.info(f"Starting {export_type} data export (Session: {self.export_session_id})")

            # 1. Get items
            items = self._get_items()
            if not items:
                return self.export_metadata

            # 2. Filter items
            filtered_items = self._filter_items(items)
            if not filtered_items:
                return self.export_metadata

            # 3. Request exports
            if not self._request_exports(filtered_items):
                return self.export_metadata

            # 4. Wait for completion
            completed_exports, failed_export_ids = self._wait_for_exports_completion()

            # 5. Download exports
            downloaded_files = self._download_exports(completed_exports)

            # 6. Extract and merge files
            if downloaded_files:
                self._extract_export_files()
                self._merge_extracted_files()

            # 7. Update metadata
            self._update_metadata(completed_exports, failed_export_ids, filtered_items)

            # 8. Save metadata
            self._save_export_metadata()

            # 9. Log summary
            self._log_export_summary()

            return self.export_metadata

        except Exception as e:
            self.logger.error(f"Export process failed: {str(e)}")
            raise

    def _get_items(self) -> List:
        """Get items from exporter and update metadata."""
        items = self.exporter.get_items()
        self.export_metadata.total_surveys = len(items)

        if not items:
            export_type = self.exporter.get_export_type()
            self.logger.warning(f"No {export_type} items found")

        return items

    def _filter_items(self, items: List) -> List:
        """Filter items and log summary."""
        filtered_items = self.exporter.filter_items(items)

        if not filtered_items:
            self.logger.warning("No items match the filter criteria")
        else:
            export_type = self.exporter.get_export_type()
            self.logger.info(f"Total {export_type} data to be exported: {len(filtered_items)} items")

        return filtered_items

    def _request_exports(self, filtered_items: List) -> bool:
        """
        Request exports for filtered items, handling date range splitting if needed.

        Args:
            filtered_items: List of items to export

        Returns:
            True if any exports were requested, False otherwise
        """
        # Get the date range from configuration
        date_range = self.config_manager.get_date_range()
        start_time = date_range["start_time"]
        end_time = date_range["end_time"]

        # Check if date range needs splitting (>6 months)
        date_range_duration = end_time - start_time
        needs_splitting = date_range_duration > TimeConstants.MS_PER_6_MONTHS

        if needs_splitting:
            self.logger.info(
                f"Date range ({date_range_duration / TimeConstants.MS_PER_DAY:.1f} days) exceeds 6 months. "
                f"Splitting into chunks."
            )
            date_chunks = self.split_date_range_into_chunks(start_time, end_time)
            self.logger.info(f"Split date range into {len(date_chunks)} chunks")
        else:
            date_chunks = [{"start_time": start_time, "end_time": end_time}]

        # Request exports for each item and chunk
        for i, item in enumerate(filtered_items):
            # Initialize item in metadata with empty export details
            item_dict = asdict(item) if hasattr(item, '__dataclass_fields__') else {'item': str(item)}
            item_dict['export_details'] = []
            self.export_metadata.surveys.append(item_dict)

            for j, chunk in enumerate(date_chunks):
                try:
                    chunk_start = chunk["start_time"]
                    chunk_end = chunk["end_time"]

                    # Create export request for this chunk
                    export_request = self.exporter.create_export_request(item, chunk)

                    # Log request
                    item_name = self.exporter.get_item_display_name(item)
                    if needs_splitting:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_items)}][{j + 1}/{len(date_chunks)}] "
                            f"Requesting export for {item_name} - "
                            f"Date range: {datetime.fromtimestamp(chunk_start / 1000, tz=timezone.utc).strftime('%Y-%m-%d')} "
                            f"to {datetime.fromtimestamp(chunk_end / 1000, tz=timezone.utc).strftime('%Y-%m-%d')}"
                        )
                    else:
                        self.logger.info(f"[{i + 1}/{len(filtered_items)}] Requesting export for {item_name}")

                    # Request export
                    export_id = self.exporter.request_export(item, export_request)

                    # Create export detail with chunk information
                    export_detail = {
                        "exportId": export_id,
                        "chunk_start": chunk_start,
                        "chunk_end": chunk_end,
                        "chunk_index": j if needs_splitting else 0,
                        "total_chunks": len(date_chunks) if needs_splitting else 1,
                        "status": None,
                        "file_path": None
                    }

                    # Add export detail to the item in metadata
                    item_dict['export_details'].append(export_detail)

                    if needs_splitting:
                        self.logger.info(
                            f"[{i + 1}/{len(filtered_items)}][{j + 1}/{len(date_chunks)}] "
                            f"Requested export, export id: {export_id}"
                        )
                    else:
                        self.logger.info(f"[{i + 1}/{len(filtered_items)}] Requested export, export id: {export_id}")

                    time.sleep(0.5)

                except Exception as e:
                    item_id = self.exporter.get_item_identifier(item)
                    self.logger.error(ErrorMessages.EXPORT_REQUEST_FAILED.format(
                        survey_id=item_id, error=str(e)
                    ))
                    self.export_metadata.failures.append({
                        "itemId": item_id,
                        "error": str(e),
                        "stage": "export_request",
                        "chunk_index": j if needs_splitting else None
                    })

        # Check if any exports were successfully requested
        total_exports = sum(len(item['export_details']) for item in self.export_metadata.surveys)
        if total_exports == 0:
            self.logger.error("No exports were successfully requested")
            return False
        else:
            self.logger.info(f"Successfully requested {total_exports} exports")
            return True

    def _wait_for_exports_completion(self) -> Tuple[Dict[str, any], List[str]]:
        """
        Wait for all exports to complete and return completed and failed exports.

        Returns:
            Tuple of (completed_exports dict, failed_export_ids list)
        """
        completed_exports = {}
        failed_exports = []

        # Flatten all export IDs from all items in metadata
        all_export_ids = []
        for item in self.export_metadata.surveys:
            for export_detail in item['export_details']:
                all_export_ids.append(export_detail['exportId'])

        pending_exports = set(all_export_ids)
        start_wait_time = time.time()

        # Initialize cumulative status counts
        cumulative_status_counts = {"COMPLETED": 0, "FAILED": 0, "IN_PROGRESS": len(pending_exports)}

        self.logger.info(f"Checking Export Status: Waiting for {len(pending_exports)} exports to complete")

        while pending_exports:
            # Check if we've exceeded max wait time
            if self.max_wait_time and (time.time() - start_wait_time) > self.max_wait_time:
                self.logger.warning(
                    f"Maximum wait time ({self.max_wait_time}s) exceeded. "
                    f"{len(pending_exports)} exports still pending."
                )
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
                f"Status after this check: TOTAL: {len(all_export_ids)}, "
                f"COMPLETED: {cumulative_status_counts['COMPLETED']}, "
                f"FAILED: {cumulative_status_counts['FAILED']}, "
                f"IN_PROGRESS: {cumulative_status_counts['IN_PROGRESS']}"
            )

        return completed_exports, failed_exports

    def _download_exports(self, completed_exports: Dict) -> List[Path]:
        """
        Download completed exports.

        Args:
            completed_exports: Dictionary mapping export_id to ExportStatus

        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        for i, (export_id, status) in enumerate(completed_exports.items(), start=1):
            try:
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloading export: {export_id}")
                file_path = self.client.download_export(export_id, self.output_dir)
                relative_path = os.path.relpath(file_path, start=os.getcwd())
                self.logger.info(f"[{i}/{len(completed_exports)}] Downloaded: {relative_path}")
                downloaded_files.append(file_path)

                # Find and update the export detail in metadata
                for item in self.export_metadata.surveys:
                    for export_detail in item['export_details']:
                        if export_detail['exportId'] == export_id:
                            export_detail['status'] = asdict(status)
                            export_detail['file_path'] = str(file_path)
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

    def _extract_export_files(self) -> None:
        """Extract export files from ZIP archives."""
        if not self.extract_files:
            self.logger.info("File extraction disabled in configuration")
            return

        self.logger.info(f"Extracting {self.export_format} files from zip archives")

        # Track extracted filenames to handle conflicts
        extracted_filenames = {}

        # Process all items and their export details
        for item in self.export_metadata.surveys:
            for export_detail in item['export_details']:
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

                            # Show path relative to current working directory
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

    def _merge_extracted_files(self) -> None:
        """Merge extracted files for items with multiple exports (JSON only)."""
        # Only merge JSON files
        if self.export_format != "JSON":
            return

        # Group extracted files by item
        for item in self.export_metadata.surveys:
            export_details = item.get('export_details', [])
            if len(export_details) <= 1:
                continue  # No merging needed for single export

            # Collect file paths
            file_paths = []
            for export_detail in export_details:
                file_path = export_detail.get('file_path')
                if file_path:
                    # Find extracted JSON file
                    chunk_index = export_detail.get('chunk_index', 0)
                    # Look for pattern like *_part_N.json in output directory
                    for extracted_file in self.output_dir.glob(f"*_part_{chunk_index + 1}.json"):
                        file_paths.append(extracted_file)
                        break

            if len(file_paths) > 1:
                # Merge files
                item_id = self.exporter.get_item_identifier(item)
                self.logger.info(f"Merging {len(file_paths)} files for item {item_id}")

                merged_filename = f"item_{item_id}_merged.json"
                merged_path = self.output_dir / merged_filename

                if self._merge_json_files(file_paths, merged_path):
                    self.logger.info(f"Successfully merged files for item {item_id} to: {merged_path}")
                    # Update metadata
                    for export_detail in export_details:
                        export_detail["merged_file"] = str(merged_path)
                else:
                    self.logger.error(f"Failed to merge files for item {item_id}")

    @staticmethod
    def _merge_json_files(file_paths: List[Path], output_path: Path) -> bool:
        """
        Merge multiple JSON files into a single file.

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

    def _update_metadata(self, completed_exports: Dict, failed_export_ids: List, filtered_items: List) -> None:
        """Update export metadata with final statistics."""
        self.export_metadata.successful_exports = len(completed_exports)
        self.export_metadata.failed_exports = len(failed_export_ids) + len(self.export_metadata.failures)

        # Check metadata configuration
        metadata_config = self.config_manager.get_metadata_config()
        include_item_details = metadata_config.get("include_survey_details", True)
        include_export_status = metadata_config.get("include_export_status", True)

        # If item details are disabled, clear the list
        if not include_item_details:
            self.export_metadata.surveys = []
        elif not include_export_status:
            # Keep items but clear export details
            for item in self.export_metadata.surveys:
                item['export_details'] = []

        end_time = datetime.now(timezone.utc)
        self.export_metadata.end_timestamp = end_time.isoformat()
        self.export_metadata.duration_seconds = (end_time - self.start_time).total_seconds()

    def _save_export_metadata(self) -> None:
        """Save export metadata to JSON file."""
        metadata_config = self.config_manager.get_metadata_config()

        if not metadata_config.get("save_metadata", True):
            self.logger.info("Metadata saving disabled in configuration")
            return

        metadata_filename = metadata_config.get("filename", FileConstants.DEFAULT_METADATA_FILENAME)
        metadata_file = self.output_dir / metadata_filename

        try:
            with open(metadata_file, 'w') as f:
                json.dump(asdict(self.export_metadata), f, indent=2)

            # Show path relative to current working directory
            relative_path = os.path.relpath(metadata_file, start=os.getcwd())
            self.logger.info(SuccessMessages.METADATA_SAVED.format(file_path=relative_path))
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {str(e)}")

    def _log_export_summary(self) -> None:
        """Log summary of the export process."""
        export_type = self.exporter.get_export_type()
        self.logger.info(SuccessMessages.EXPORT_COMPLETED)
        self.logger.info(f"Export type: {export_type}")
        self.logger.info(f"Total items: {self.export_metadata.total_surveys}")
        self.logger.info(f"Successful exports: {self.export_metadata.successful_exports}")
        self.logger.info(f"Failed exports: {len(self.export_metadata.failures)}")

        # Show details about multiple exports per item
        total_export_requests = sum(len(item.get('export_details', [])) for item in self.export_metadata.surveys)
        if total_export_requests > self.export_metadata.total_surveys:
            self.logger.info(
                f"Total export requests: {total_export_requests} "
                f"(multiple exports per item due to date range splitting)"
            )

        self.logger.info(f"Duration: {self.export_metadata.duration_seconds:.2f} seconds")
        self.logger.info(f"Output directory: {self.output_dir}")
