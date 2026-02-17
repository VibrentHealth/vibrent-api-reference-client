#!/usr/bin/env python3
"""
Example script demonstrating Participant Profiles (User Properties) exports

This script shows how to:
1. Export ALL participants in the program
2. Export specific participants
3. Use batch exports (multiple participants in one request)
4. Handle the 1000 participant API limit
5. Apply participant filtering
6. Use the factory pattern
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.client import VibrentHealthAPIClient
from vibrent_api_client.exporters.participant_profiles_exporter import ParticipantProfilesExporter
from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.utils.helpers import setup_logging


def example_export_all_participants():
    """Example 1: Export ALL participants in the program"""
    print("\n=== Example 1: Export ALL Participants ===")
    print("Export profile data for all participants in the authenticated program")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure to export all participants
        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,  # Profiles don't use date ranges
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [],  # Empty = export ALL
                "max_participants": None,
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export using orchestrator
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles for all participants")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_specific_participants():
    """Example 2: Export specific participants"""
    print("\n=== Example 2: Export Specific Participants ===")
    print("Export profile data for a specific list of participants")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure to export specific participants
        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890, 11111, 22222, 33333],  # Specific IDs
                "max_participants": None,
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles for {metadata.successful_exports} batch(es)")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_large_batch_export():
    """Example 3: Export large batch of participants (demonstrating 1000 limit)"""
    print("\n=== Example 3: Large Batch Export ===")
    print("Export profile data for many participants (max 1000 per request)")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Create a large list of participant IDs (for demonstration)
        # In real usage, these would be actual participant IDs from your program
        large_participant_list = list(range(1, 501))  # 500 participants

        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": large_participant_list,
                "max_participants": None,
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles for {len(large_participant_list)} participants in single batch")
        print(f"Successful exports: {metadata.successful_exports}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_with_exclusions():
    """Example 4: Export with participant exclusions"""
    print("\n=== Example 4: Export with Exclusions ===")
    print("Export profiles while excluding specific participants")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with exclusions
        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890, 11111, 22222, 33333, 44444],
                "max_participants": None,
                "exclude_participant_ids": [22222, 44444]  # Exclude these two
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles (excluding 2 participants)")
        print(f"Expected: 4 participants after exclusions")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_with_max_limit():
    """Example 5: Export with maximum participant limit"""
    print("\n=== Example 5: Export with Max Limit ===")
    print("Export profiles with a maximum participant limit")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with max limit
        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": list(range(1, 101)),  # 100 participants
                "max_participants": 10,  # Only export first 10
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles for first 10 participants (out of 100 configured)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_using_factory_pattern():
    """Example 6: Using ExporterFactory to create participant profiles exporter"""
    print("\n=== Example 6: Using Factory Pattern ===")
    print("Demonstrate using ExporterFactory for participant profiles exports")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure participant profiles export
        config_manager.update_config({
            "export": {
                "type": "participant_profiles"  # Factory will auto-create exporter
            },
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890],
                "max_participants": None,
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        # Use factory to create the right exporter automatically
        from vibrent_api_client.core.exporter_factory import ExporterFactory

        client = VibrentHealthAPIClient(config_manager)
        export_type = config_manager.get("export.type", "survey")

        # Factory automatically creates ParticipantProfilesExporter
        exporter = ExporterFactory.create_exporter(export_type, client, config_manager)

        print(f"Factory created: {exporter.__class__.__name__}")

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported profiles for {metadata.successful_exports} batch(es)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_api_limit_warning():
    """Example 7: Demonstrate handling of 1000 participant API limit"""
    print("\n=== Example 7: API Limit Warning ===")
    print("Show how the exporter handles exceeding the 1000 participant limit")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Create a list exceeding 1000 participants (for demonstration)
        # In real usage, the exporter will warn and truncate
        oversized_list = list(range(1, 1501))  # 1500 participants

        config_manager.update_config({
            "participant_profiles_export": {
                "use_date_range": False,
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": oversized_list,
                "max_participants": None,
                "exclude_participant_ids": None
            }
        })

        # Setup logging
        setup_logging()

        print(f"\nConfigured {len(oversized_list)} participants (exceeds API limit of 1000)")
        print("Exporter will automatically truncate to first 1000 and log a warning")

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = ParticipantProfilesExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed!")
        print(f"Check logs for truncation warning")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all examples"""
    print("=" * 80)
    print("Vibrent Health API Client - Participant Profiles Export Examples")
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
        # Example 1: Export all participants
        # example_export_all_participants()

        # Example 2: Export specific participants
        # example_export_specific_participants()

        # Example 3: Large batch export
        # example_large_batch_export()

        # Example 4: With exclusions
        # example_with_exclusions()

        # Example 5: With max limit
        # example_with_max_limit()

        # Example 6: Factory pattern
        example_using_factory_pattern()

        # Example 7: API limit warning
        # example_api_limit_warning()

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
