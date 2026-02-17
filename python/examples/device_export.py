#!/usr/bin/env python3
"""
Example script demonstrating Device Data exports

This script shows how to:
1. Configure device data exports for specific participants
2. Use the new DeviceExporter with the extensible architecture
3. Filter by device type (FITBIT, GARMIN, APPLE_HEALTHKIT)
4. Filter by data type (SLEEP, HEART_RATE, STEPS, etc.)
5. Use manifest-only exports
6. Handle participant filtering
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.client import VibrentHealthAPIClient
from vibrent_api_client.exporters.device_exporter import DeviceExporter
from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.utils.helpers import setup_logging


def example_basic_device_export():
    """Example 1: Basic device export for a single participant (all devices, all data types)"""
    print("\n=== Example 1: Basic Device Export (Single Participant, All Data) ===")
    print("Export all device data for one participant")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for device export
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30  # Last 30 days
                },
                "split_date_range": True,
                "participant_ids": [12345],  # Single participant
                "max_participants": None,
                "exclude_participant_ids": None,
                "device_types": [],  # Empty = all device types
                "data_types": [],    # Empty = all data types
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager, environment="staging")
        exporter = DeviceExporter(client, config_manager)

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


def example_fitbit_sleep_only():
    """Example 2: Export only Fitbit sleep data"""
    print("\n=== Example 2: Fitbit Sleep Data Only ===")
    print("Export sleep data from Fitbit devices for one participant")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for Fitbit sleep only
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 7  # Last 7 days
                },
                "split_date_range": False,  # Don't split for short range
                "participant_ids": [12345],
                "device_types": ["FITBIT"],  # Only Fitbit
                "data_types": ["SLEEP"],     # Only sleep data
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported Fitbit sleep data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_multiple_device_types():
    """Example 3: Export data from multiple device types"""
    print("\n=== Example 3: Multiple Device Types ===")
    print("Export heart rate and activity data from Fitbit and Garmin")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for multiple device types and data types
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 14  # Last 2 weeks
                },
                "split_date_range": False,
                "participant_ids": [12345, 67890],
                "device_types": ["FITBIT", "GARMIN"],  # Fitbit and Garmin
                "data_types": ["HEART_RATE", "ACTIVITY"],  # Heart rate and activity
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

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


def example_apple_healthkit_all_types():
    """Example 4: Export all data types from Apple HealthKit"""
    print("\n=== Example 4: Apple HealthKit - All Data Types ===")
    print("Export all available data types from Apple HealthKit")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for Apple HealthKit with all data types
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30
                },
                "split_date_range": True,
                "participant_ids": [12345],
                "device_types": ["APPLE_HEALTHKIT"],  # Only Apple HealthKit
                "data_types": [],  # All data types (empty = all)
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported Apple HealthKit data for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_manifest_only():
    """Example 5: Export manifest only (metadata without data files)"""
    print("\n=== Example 5: Manifest-Only Export ===")
    print("Export only manifest metadata without full data files")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for manifest-only export
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 90
                },
                "split_date_range": True,
                "participant_ids": [12345, 67890],
                "device_types": [],  # All device types
                "data_types": [],    # All data types
                "manifest_only": True  # Only manifest
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nManifest-only export completed successfully!")
        print(f"Exported manifest for {metadata.successful_exports} participant(s)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_comprehensive_filter():
    """Example 6: Comprehensive filtering example"""
    print("\n=== Example 6: Comprehensive Filtering ===")
    print("Export with multiple filters: device types, data types, date range, participant exclusions")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with comprehensive filters
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 60  # Last 60 days
                },
                "split_date_range": True,
                "participant_ids": [12345, 67890, 11111, 22222],
                "max_participants": 3,  # Limit to first 3
                "exclude_participant_ids": [22222],  # Exclude this one
                "device_types": ["FITBIT", "APPLE_HEALTHKIT"],  # Fitbit and Apple only
                "data_types": ["SLEEP", "STEPS", "HEART_RATE"],  # Specific data types
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

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
    """Example 7: Using ExporterFactory to create device exporter"""
    print("\n=== Example 7: Using Factory Pattern ===")
    print("Demonstrate using ExporterFactory for device exports")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure device export in config
        config_manager.update_config({
            "export": {
                "type": "device"  # Factory will auto-create DeviceExporter
            },
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30
                },
                "participant_ids": [12345],
                "device_types": ["FITBIT"],
                "data_types": ["SLEEP", "HEART_RATE"],
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Use factory to create the right exporter automatically
        from vibrent_api_client.core.exporter_factory import ExporterFactory

        client = VibrentHealthAPIClient(config_manager)
        export_type = config_manager.get("export.type", "survey")

        # Factory automatically creates DeviceExporter based on config
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


def example_absolute_date_range():
    """Example 8: Export with absolute date range"""
    print("\n=== Example 8: Device Export with Absolute Date Range ===")
    print("Export device data for specific date range (January 2024)")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with absolute dates
        config_manager.update_config({
            "device_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30,
                    "absolute_start_date": "2024-01-01",
                    "absolute_end_date": "2024-01-31"
                },
                "split_date_range": False,
                "participant_ids": [12345],
                "device_types": [],
                "data_types": [],
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = DeviceExporter(client, config_manager)

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
    print("Vibrent Health API Client - Device Data Export Examples")
    print("=" * 80)

    # Check for required environment variables
    required_env_vars = ["VIBRENT_CLIENT_ID", "VIBRENT_CLIENT_SECRET"]
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
        # Example 1: Basic all-data export
        # example_basic_device_export()

        # Example 2: Fitbit sleep only
        # example_fitbit_sleep_only()

        # Example 3: Multiple device types
        # example_multiple_device_types()

        # Example 4: Apple HealthKit all types
        # example_apple_healthkit_all_types()

        # Example 5: Manifest only
        # example_manifest_only()

        # Example 6: Comprehensive filtering
        # example_comprehensive_filter()

        # Example 7: Factory pattern
        example_using_factory_pattern()

        # Example 8: Absolute date range
        # example_absolute_date_range()

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
