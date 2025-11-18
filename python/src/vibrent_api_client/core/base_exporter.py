"""
Base exporter class for Vibrent Health API Client

This module defines the abstract base class that all exporters must implement.
It provides the contract for export-specific logic while allowing the orchestrator
to handle common workflow operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .client import VibrentHealthAPIClient
from .config import ConfigManager


class BaseExporter(ABC):
    """
    Abstract base class for all export types.

    This class defines the interface that all exporters must implement. It separates
    export-specific logic (what to export, how to filter, which API to call) from
    common workflow logic (polling, downloading, metadata).

    Usage:
        class MyExporter(BaseExporter):
            def get_export_type(self) -> str:
                return "my_export_type"

            def get_items(self) -> List[Any]:
                # Fetch items to export
                return items

            # ... implement other abstract methods

    Attributes:
        client: The API client for making requests
        config_manager: Configuration manager for accessing settings
        logger: Logger instance for this exporter
    """

    def __init__(self, client: VibrentHealthAPIClient, config_manager: ConfigManager):
        """
        Initialize the base exporter.

        Args:
            client: The API client instance for making API calls
            config_manager: Configuration manager for accessing settings
        """
        self.client = client
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)

        # Log initialization
        self.logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def get_export_type(self) -> str:
        """
        Get the export type identifier.

        This identifier is used for:
        - Configuration lookup (e.g., export.survey, export.ehr)
        - Logging and metadata tracking
        - Output directory naming

        Returns:
            Export type identifier (e.g., 'survey', 'ehr', 'device')

        Example:
            >>> exporter.get_export_type()
            'survey'
        """
        pass

    @abstractmethod
    def get_items(self) -> List[Any]:
        """
        Fetch the items to export.

        This method retrieves the list of items that can be exported. For example:
        - Survey exporter: returns list of Survey objects
        - EHR exporter: returns list of Participant objects
        - Device exporter: returns list of Device objects

        Returns:
            List of items that can be exported. The type depends on the exporter.

        Raises:
            VibrentHealthAPIError: If API call fails

        Example:
            >>> surveys = exporter.get_items()
            >>> len(surveys)
            42
        """
        pass

    @abstractmethod
    def filter_items(self, items: List[Any]) -> List[Any]:
        """
        Apply configuration-based filtering to items.

        This method filters the items based on configuration settings such as:
        - Inclusion lists (specific IDs to include)
        - Exclusion lists (specific IDs to exclude)
        - Maximum number of items
        - Other criteria specific to the export type

        Args:
            items: List of items to filter

        Returns:
            Filtered list of items to export

        Example:
            >>> all_surveys = [survey1, survey2, survey3]
            >>> filtered = exporter.filter_items(all_surveys)
            >>> len(filtered)
            2
        """
        pass

    @abstractmethod
    def create_export_request(self, item: Any, date_range: Dict[str, int]) -> Any:
        """
        Create an export request object for a single item.

        This method constructs the request object needed for the API call. It should
        use both the item details and the date range to create a properly formatted
        request.

        Args:
            item: The item to export (e.g., Survey, Participant)
            date_range: Dictionary with 'start_time' and 'end_time' in milliseconds

        Returns:
            Export request object (type depends on export type, e.g., ExportRequest)

        Example:
            >>> date_range = {'start_time': 1704067200000, 'end_time': 1706745600000}
            >>> request = exporter.create_export_request(survey, date_range)
            >>> request.dateFrom
            1704067200000
        """
        pass

    @abstractmethod
    def request_export(self, item: Any, export_request: Any) -> str:
        """
        Request export via API and return export ID.

        This method makes the actual API call to request the export. It should
        call the appropriate API endpoint for this export type.

        Args:
            item: The item being exported (for logging/tracking)
            export_request: The export request object created by create_export_request

        Returns:
            Export ID string that can be used to track the export status

        Raises:
            VibrentHealthAPIError: If API call fails

        Example:
            >>> export_id = exporter.request_export(survey, request)
            >>> export_id
            '123e4567-e89b-12d3-a456-426614174000'
        """
        pass

    @abstractmethod
    def get_item_identifier(self, item: Any) -> str:
        """
        Get unique identifier for an item.

        This identifier is used for:
        - Logging which item is being processed
        - Tracking in metadata
        - Debugging and troubleshooting

        Args:
            item: The item to get identifier from

        Returns:
            String identifier that uniquely identifies the item

        Example:
            >>> exporter.get_item_identifier(survey)
            '1234'
        """
        pass

    @abstractmethod
    def get_item_display_name(self, item: Any) -> str:
        """
        Get human-readable display name for an item.

        This name is used for:
        - User-facing log messages
        - Progress reporting
        - Metadata display

        Args:
            item: The item to get display name from

        Returns:
            Human-readable string describing the item

        Example:
            >>> exporter.get_item_display_name(survey)
            'Cancer History Survey (ID: 1234)'
        """
        pass

    def get_config_section(self) -> Dict[str, Any]:
        """
        Get the configuration section for this export type.

        This is a convenience method that retrieves the export-type-specific
        configuration section (e.g., export.survey, export.ehr).

        Returns:
            Dictionary containing export-type-specific configuration

        Example:
            >>> config = exporter.get_config_section()
            >>> config.get('format')
            'JSON'
        """
        export_type = self.get_export_type()
        return self.config_manager.get(f"export.{export_type}", {})

    def should_extract_files(self) -> bool:
        """
        Check if files should be extracted from ZIP archives.

        This checks the global output configuration to determine if extraction
        is enabled.

        Returns:
            True if files should be extracted, False otherwise
        """
        output_config = self.config_manager.get_output_config()
        return output_config.get("extract_files", True)

    def get_output_directory_name(self) -> str:
        """
        Get the output directory name for this export type.

        This returns the configured directory name for this export type's outputs.
        For example: 'survey_exports', 'ehr_exports', etc.

        Returns:
            Directory name string

        Example:
            >>> exporter.get_output_directory_name()
            'survey_exports'
        """
        export_type = self.get_export_type()
        output_config = self.config_manager.get_output_config()
        dir_key = f"{export_type}_exports_dir"

        # Fallback to generic naming if not configured
        default_dir = f"{export_type}_exports"
        return output_config.get(dir_key, default_dir)

    def validate_items(self, items: List[Any]) -> bool:
        """
        Validate that items list is suitable for export.

        This method performs basic validation on the items list. Subclasses can
        override this for more specific validation.

        Args:
            items: List of items to validate

        Returns:
            True if items are valid, False otherwise

        Example:
            >>> items = exporter.get_items()
            >>> if exporter.validate_items(items):
            ...     proceed_with_export()
        """
        if not items:
            self.logger.warning(f"No items found for {self.get_export_type()} export")
            return False

        if not isinstance(items, list):
            self.logger.error(f"Items must be a list, got {type(items)}")
            return False

        return True

    def log_export_summary(self, total_items: int, filtered_items: int, export_count: int) -> None:
        """
        Log a summary of the export operation.

        This is a convenience method for consistent logging across exporters.

        Args:
            total_items: Total number of items available
            filtered_items: Number of items after filtering
            export_count: Number of exports actually requested
        """
        export_type = self.get_export_type()
        self.logger.info(f"{export_type.capitalize()} Export Summary:")
        self.logger.info(f"  Total {export_type}s available: {total_items}")
        self.logger.info(f"  After filtering: {filtered_items}")
        self.logger.info(f"  Export requests created: {export_count}")
