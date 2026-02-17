#!/usr/bin/env python3
"""
Example script demonstrating EHR (Electronic Health Record) data exports

This script shows how to:
1. Configure EHR exports for specific participants
2. Use the new EHRExporter with the extensible architecture
3. Handle participant filtering
4. Export EHR data for multiple participants
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.client import VibrentHealthAPIClient
from vibrent_api_client.exporters.ehr_exporter import EHRExporter
from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.utils.helpers import setup_logging_from_config


def example_basic_ehr_export():
    """Example 1: Basic EHR export for a single participant"""
    print("\n=== Example 1: Basic EHR Export (Single Participant) ===")
    print("Export EHR data for one participant using default date range")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for EHR export
        config_manager.update_config({
            "export": {
                "type": "ehr",  # Switch to EHR export type
                "date_range": {
                    "default_days_back": 30  # Last 30 days
                },
                "ehr": {
                    "participant_ids": [12345],  # Single participant
                    "max_participants": None,
                    "exclude_participant_ids": None
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)

        # Run export using orchestrator
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_multiple_participants():
    """Example 2: Export EHR data for multiple participants"""
    print("\n=== Example 2: Multiple Participants EHR Export ===")
    print("Export EHR data for multiple participants")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for multiple participants
        config_manager.update_config({
            "export": {
                "type": "ehr",
                "date_range": {
                    "default_days_back": 60  # Last 60 days
                },
                "ehr": {
                    "participant_ids": [12345, 67890, 11111],  # Multiple participants
                    "max_participants": None,
                    "exclude_participant_ids": None
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")
        if metadata.failed_exports > 0:
            print(f"Failed exports: {metadata.failed_exports}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_with_exclusions():
    """Example 3: Export with participant exclusions"""
    print("\n=== Example 3: EHR Export with Exclusions ===")
    print("Export EHR data while excluding specific participants")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with exclusions
        config_manager.update_config({
            "export": {
                "type": "ehr",
                "date_range": {
                    "default_days_back": 90  # Last 90 days
                },
                "ehr": {
                    "participant_ids": [12345, 67890, 11111, 22222, 33333],
                    "max_participants": None,
                    "exclude_participant_ids": [22222]  # Exclude this participant
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_with_max_limit():
    """Example 4: Export with maximum participant limit"""
    print("\n=== Example 4: EHR Export with Max Limit ===")
    print("Export EHR data with a maximum participant limit")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with max limit
        config_manager.update_config({
            "export": {
                "type": "ehr",
                "date_range": {
                    "default_days_back": 30
                },
                "ehr": {
                    "participant_ids": [12345, 67890, 11111, 22222, 33333, 44444],
                    "max_participants": 3,  # Only export first 3
                    "exclude_participant_ids": None
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_absolute_date_range():
    """Example 5: Export with absolute date range"""
    print("\n=== Example 5: EHR Export with Absolute Date Range ===")
    print("Export EHR data for specific date range (January 2024)")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with absolute dates
        config_manager.update_config({
            "export": {
                "type": "ehr",
                "date_range": {
                    "default_days_back": 30,
                    "absolute_start_date": "2024-01-01",
                    "absolute_end_date": "2024-01-31"
                },
                "ehr": {
                    "participant_ids": [12345, 67890],
                    "max_participants": None,
                    "exclude_participant_ids": None
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = EHRExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_using_factory_pattern():
    """Example 6: Using ExporterFactory to create EHR exporter"""
    print("\n=== Example 6: Using Factory Pattern ===")
    print("Demonstrate using ExporterFactory for EHR exports")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure EHR export in config file (or programmatically)
        config_manager.update_config({
            "export": {
                "type": "ehr",  # Factory will auto-create EHRExporter
                "date_range": {
                    "default_days_back": 30
                },
                "ehr": {
                    "participant_ids": [12345],
                    "max_participants": None,
                    "exclude_participant_ids": None
                }
            }
        })

        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)

        # Use factory to create the right exporter automatically
        from vibrent_api_client.core.exporter_factory import ExporterFactory

        client = VibrentHealthAPIClient(config_manager)
        export_type = config_manager.get("export.type", "survey")

        # Factory automatically creates EHRExporter based on config
        exporter = ExporterFactory.create_exporter(export_type, client, config_manager)

        print(f"Factory created: {exporter.__class__.__name__}")

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all examples"""
    print("=" * 80)
    print("Vibrent Health API Client - EHR Export Examples")
    print("=" * 80)

    # Check for required environment variables
    required_env_vars = ["CLIENT_ID", "CLIENT_SECRET"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("\nWarning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nThese examples will fail without proper API credentials.")
        print("Please set them before running.")
        return

    # Run examples (uncomment the ones you want to run)
    try:
        # Example 1: Basic single participant
        # example_basic_ehr_export()

        # Example 2: Multiple participants
        # example_multiple_participants()

        # Example 3: With exclusions
        # example_with_exclusions()

        # Example 4: With max limit
        # example_with_max_limit()

        # Example 5: Absolute date range
        # example_absolute_date_range()

        # Example 6: Factory pattern
        example_using_factory_pattern()

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
