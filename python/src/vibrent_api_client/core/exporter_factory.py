"""
Exporter factory for Vibrent Health API Client

This module contains the factory class for creating appropriate exporter instances
based on export type configuration.
"""

import logging
from typing import Dict, Type

from .base_exporter import BaseExporter
from .client import VibrentHealthAPIClient
from .config import ConfigManager


class ExporterFactory:
    """
    Factory for creating exporter instances.

    This factory uses a registry pattern to manage different exporter types.
    It allows for both built-in exporters and custom exporter registration.

    Usage:
        # Create built-in exporter
        exporter = ExporterFactory.create_exporter('survey', client, config)

        # Register custom exporter
        ExporterFactory.register_exporter('custom', CustomExporter)
        exporter = ExporterFactory.create_exporter('custom', client, config)

    Attributes:
        _EXPORTER_REGISTRY: Dictionary mapping export type to exporter class
    """

    # Registry of available exporters
    # This will be populated with built-in exporters after their implementation
    _EXPORTER_REGISTRY: Dict[str, Type[BaseExporter]] = {}

    _logger = logging.getLogger(__name__)

    @classmethod
    def create_exporter(cls,
                       export_type: str,
                       client: VibrentHealthAPIClient,
                       config_manager: ConfigManager) -> BaseExporter:
        """
        Create an exporter instance for the given export type.

        Args:
            export_type: The type of exporter to create (e.g., 'survey', 'ehr')
            client: The API client instance
            config_manager: The configuration manager instance

        Returns:
            An instance of the appropriate BaseExporter subclass

        Raises:
            ValueError: If the export type is not registered

        Example:
            >>> client = VibrentHealthAPIClient(config_manager)
            >>> exporter = ExporterFactory.create_exporter('survey', client, config_manager)
            >>> exporter.get_export_type()
            'survey'
        """
        exporter_class = cls._EXPORTER_REGISTRY.get(export_type)

        if not exporter_class:
            available_types = ', '.join(cls._EXPORTER_REGISTRY.keys())
            error_message = (
                f"Unknown export type: '{export_type}'. "
                f"Available types: {available_types if available_types else 'None registered'}. "
                f"You can register custom exporters using ExporterFactory.register_exporter()."
            )
            cls._logger.error(error_message)
            raise ValueError(error_message)

        cls._logger.debug(f"Creating exporter for type: {export_type}")

        try:
            exporter = exporter_class(client, config_manager)
            cls._logger.info(f"Successfully created {exporter_class.__name__}")
            return exporter
        except Exception as e:
            error_message = f"Failed to create exporter for type '{export_type}': {str(e)}"
            cls._logger.error(error_message)
            raise RuntimeError(error_message) from e

    @classmethod
    def register_exporter(cls, export_type: str, exporter_class: Type[BaseExporter]) -> None:
        """
        Register a custom exporter class.

        This allows users to add their own exporter implementations without
        modifying the library code.

        Args:
            export_type: The export type identifier (e.g., 'custom_device')
            exporter_class: The exporter class (must inherit from BaseExporter)

        Raises:
            TypeError: If exporter_class does not inherit from BaseExporter
            ValueError: If export_type is empty or invalid

        Example:
            >>> class CustomExporter(BaseExporter):
            ...     # implementation
            ...     pass
            >>> ExporterFactory.register_exporter('custom', CustomExporter)
            >>> exporter = ExporterFactory.create_exporter('custom', client, config)
        """
        # Validate export type
        if not export_type or not isinstance(export_type, str):
            raise ValueError("Export type must be a non-empty string")

        # Validate exporter class
        if not isinstance(exporter_class, type):
            raise TypeError(f"exporter_class must be a class, not {type(exporter_class)}")

        if not issubclass(exporter_class, BaseExporter):
            raise TypeError(
                f"exporter_class must inherit from BaseExporter. "
                f"{exporter_class.__name__} does not inherit from BaseExporter."
            )

        # Warn if overwriting existing registration
        if export_type in cls._EXPORTER_REGISTRY:
            cls._logger.warning(
                f"Overwriting existing exporter registration for type '{export_type}'. "
                f"Previous: {cls._EXPORTER_REGISTRY[export_type].__name__}, "
                f"New: {exporter_class.__name__}"
            )

        cls._EXPORTER_REGISTRY[export_type] = exporter_class
        cls._logger.info(f"Registered exporter '{exporter_class.__name__}' for type '{export_type}'")

    @classmethod
    def unregister_exporter(cls, export_type: str) -> bool:
        """
        Unregister an exporter type.

        Args:
            export_type: The export type to unregister

        Returns:
            True if the exporter was unregistered, False if it wasn't registered

        Example:
            >>> ExporterFactory.unregister_exporter('custom')
            True
        """
        if export_type in cls._EXPORTER_REGISTRY:
            exporter_class = cls._EXPORTER_REGISTRY[export_type]
            del cls._EXPORTER_REGISTRY[export_type]
            cls._logger.info(f"Unregistered exporter '{exporter_class.__name__}' for type '{export_type}'")
            return True
        else:
            cls._logger.warning(f"Cannot unregister: export type '{export_type}' is not registered")
            return False

    @classmethod
    def get_registered_types(cls) -> list:
        """
        Get a list of all registered export types.

        Returns:
            List of registered export type identifiers

        Example:
            >>> ExporterFactory.get_registered_types()
            ['survey', 'survey_v2', 'ehr']
        """
        return list(cls._EXPORTER_REGISTRY.keys())

    @classmethod
    def is_registered(cls, export_type: str) -> bool:
        """
        Check if an export type is registered.

        Args:
            export_type: The export type to check

        Returns:
            True if the export type is registered, False otherwise

        Example:
            >>> ExporterFactory.is_registered('survey')
            True
            >>> ExporterFactory.is_registered('unknown')
            False
        """
        return export_type in cls._EXPORTER_REGISTRY

    @classmethod
    def get_exporter_class(cls, export_type: str) -> Type[BaseExporter]:
        """
        Get the exporter class for a given export type without instantiating it.

        Args:
            export_type: The export type identifier

        Returns:
            The exporter class

        Raises:
            ValueError: If the export type is not registered

        Example:
            >>> exporter_class = ExporterFactory.get_exporter_class('survey')
            >>> exporter_class.__name__
            'SurveyExporter'
        """
        if export_type not in cls._EXPORTER_REGISTRY:
            available_types = ', '.join(cls._EXPORTER_REGISTRY.keys())
            raise ValueError(
                f"Unknown export type: '{export_type}'. "
                f"Available types: {available_types if available_types else 'None registered'}"
            )

        return cls._EXPORTER_REGISTRY[export_type]


# Note: Concrete exporters (SurveyExporter, EHRExporter, etc.) will be registered
# when their modules are imported. See exporters/__init__.py for registration.
