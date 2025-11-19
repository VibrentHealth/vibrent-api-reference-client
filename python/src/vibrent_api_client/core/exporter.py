"""
Survey data exporter for Vibrent Health APIs

DEPRECATED: This module is maintained for backward compatibility only.
Please use ExportOrchestrator with SurveyExporter instead.

Example:
    from vibrent_api_client.core.orchestrator import ExportOrchestrator
    from vibrent_api_client.exporters import SurveyExporter

    exporter = SurveyExporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()
"""

import warnings
import logging
from typing import Optional

from .client import VibrentHealthAPIClient
from .config import ConfigManager
from .orchestrator import ExportOrchestrator
from ..models import ExportMetadata


class SurveyDataExporter:
    """
    Legacy survey data exporter - DEPRECATED

    This class is maintained for backward compatibility only. New code should use
    ExportOrchestrator with SurveyExporter instead.

    The class now delegates all operations to the new architecture internally,
    so behavior should be identical to the previous implementation.

    Deprecated:
        Version 2.0: Use ExportOrchestrator with SurveyExporter instead

    Example (old way - still works):
        exporter = SurveyDataExporter(config_manager)
        exporter.run_export()

    Example (new way - recommended):
        client = VibrentHealthAPIClient(config_manager)
        exporter = SurveyExporter(client, config_manager)
        orchestrator = ExportOrchestrator(exporter, config_manager)
        orchestrator.run_export()
    """

    def __init__(self, config_manager: ConfigManager, environment: str = None, output_base_dir: str = None):
        """
        Initialize the survey data exporter.

        Args:
            config_manager: Configuration manager instance
            environment: Environment name (optional, uses default from config if not specified)
            output_base_dir: Base directory for output files (optional)
        """
        # Issue deprecation warning
        warnings.warn(
            "SurveyDataExporter is deprecated and will be removed in version 3.0. "
            "Please use ExportOrchestrator with SurveyExporter instead. "
            "See documentation for migration guide.",
            DeprecationWarning,
            stacklevel=2
        )

        self.config_manager = config_manager
        self.environment = environment
        self.output_base_dir = output_base_dir
        self.logger = logging.getLogger(__name__)

        # Create the new architecture components
        # Delay import to avoid circular dependency
        from ..exporters import SurveyExporter

        client = VibrentHealthAPIClient(config_manager, environment)
        survey_exporter = SurveyExporter(client, config_manager)
        self._orchestrator = ExportOrchestrator(survey_exporter, config_manager, output_base_dir)

        # Expose properties from orchestrator for backward compatibility
        self.export_metadata = self._orchestrator.export_metadata
        self.output_dir = self._orchestrator.output_dir
        self.export_session_id = self._orchestrator.export_session_id

        self.logger.info("Initialized SurveyDataExporter (using new architecture internally)")

    def run_export(self) -> None:
        """
        Run the complete export process.

        This method delegates to the new ExportOrchestrator implementation.
        """
        self.logger.debug("Delegating to ExportOrchestrator.run_export()")
        result = self._orchestrator.run_export()

        # Update local references to metadata after export completes
        self.export_metadata = result

    @staticmethod
    def split_date_range_into_chunks(start_time: int, end_time: int, chunk_size_ms: int = None) -> list:
        """
        Split a date range into chunks of specified size.

        This is a static method maintained for backward compatibility.
        Now delegates to ExportOrchestrator.split_date_range_into_chunks().

        Args:
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds
            chunk_size_ms: Size of each chunk in milliseconds

        Returns:
            List of dictionaries with 'start_time' and 'end_time' for each chunk
        """
        from .constants import TimeConstants

        if chunk_size_ms is None:
            chunk_size_ms = TimeConstants.MS_PER_6_MONTHS

        return ExportOrchestrator.split_date_range_into_chunks(start_time, end_time, chunk_size_ms)

    @staticmethod
    def merge_json_files(file_paths: list, output_path) -> bool:
        """
        Merge multiple JSON files into a single file.

        This is a static method maintained for backward compatibility.
        Now delegates to ExportOrchestrator._merge_json_files().

        Args:
            file_paths: List of JSON file paths to merge
            output_path: Path for the merged output file

        Returns:
            True if merge was successful, False otherwise
        """
        from pathlib import Path

        # Convert to Path objects if needed
        file_paths = [Path(p) if not isinstance(p, Path) else p for p in file_paths]
        output_path = Path(output_path) if not isinstance(output_path, Path) else output_path

        return ExportOrchestrator._merge_json_files(file_paths, output_path)

    # Expose some orchestrator properties/methods for backward compatibility
    @property
    def client(self):
        """Get the API client instance."""
        return self._orchestrator.client

    @property
    def exporter(self):
        """Get the exporter instance."""
        return self._orchestrator.exporter

    def create_export_request(self, start_time: int = None, end_time: int = None):
        """
        Create export request based on configuration or provided date range.

        This method is maintained for backward compatibility.

        Args:
            start_time: Start timestamp in milliseconds (optional)
            end_time: End timestamp in milliseconds (optional)

        Returns:
            ExportRequest object
        """
        if start_time is None or end_time is None:
            date_range = self.config_manager.get_date_range()
        else:
            date_range = {'start_time': start_time, 'end_time': end_time}

        # Get a sample survey to create request (won't be used in new arch)
        from ..models import ExportRequest
        export_format = self.config_manager.get("export.format", "JSON")

        return ExportRequest(
            dateFrom=date_range['start_time'],
            dateTo=date_range['end_time'],
            format=export_format
        )
