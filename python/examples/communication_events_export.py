#!/usr/bin/env python3
"""
Example script demonstrating Communication Events exports

This script shows how to:
1. Export ALL communication events for all participants
2. Export events for specific participants
3. Filter by date range
4. Filter by event sources (ITERABLE, SES, TWILIO)
5. Filter by event types (EMAIL_*, SMS_*)
6. Use manifest-only exports
7. Export specific event categories (email only, SMS only)
8. Use batch exports with multiple filters
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.client import VibrentHealthAPIClient
from vibrent_api_client.exporters.communication_events_exporter import CommunicationEventsExporter
from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.utils.helpers import setup_logging
from vibrent_api_client.models import CommunicationEventSource, CommunicationEventType


def example_export_all_events():
    """Example 1: Export ALL communication events for all participants"""
    print("\n=== Example 1: Export ALL Communication Events ==")
    print("Export all email and SMS events for all participants in the program")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure to export all events for all participants
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": False,  # No date filtering
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [],  # Empty = export ALL participants
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": None,  # All sources
                "event_types": None,  # All event types
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export using orchestrator
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported all communication events for all participants")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_specific_participants_with_date_range():
    """Example 2: Export events for specific participants with date range"""
    print("\n=== Example 2: Export Events for Specific Participants with Date Range ===")
    print("Export communication events for specific participants within a date range")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for specific participants with date range
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30  # Last 30 days
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890, 11111],
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": None,
                "event_types": None,
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported events for 3 participants (last 30 days)")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_email_events_only():
    """Example 3: Export only email events (all email types)"""
    print("\n=== Example 3: Export Email Events Only ===")
    print("Export all email-related events (sent, delivery, open, click, etc.)")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for email events only
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "absolute_start_date": "2024-01-01",
                    "absolute_end_date": "2024-12-31"
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [],  # All participants
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": [
                    CommunicationEventSource.ITERABLE,
                    CommunicationEventSource.SES
                ],
                "event_types": CommunicationEventType.get_email_types(),  # All email types
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported email events only (all email types)")
        print(f"Sources: ITERABLE, SES")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_sms_events_only():
    """Example 4: Export only SMS events"""
    print("\n=== Example 4: Export SMS Events Only ===")
    print("Export all SMS-related events (send, delivered, bounce, etc.)")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for SMS events only
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 60  # Last 60 days
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890],
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": [CommunicationEventSource.TWILIO],
                "event_types": CommunicationEventType.get_sms_types(),  # All SMS types
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported SMS events only")
        print(f"Source: TWILIO")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_specific_event_types():
    """Example 5: Export specific event types (e.g., only opens and clicks)"""
    print("\n=== Example 5: Export Specific Event Types ===")
    print("Export only email open and click events")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for specific event types
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 14  # Last 2 weeks
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [],
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": None,
                "event_types": [
                    CommunicationEventType.EMAIL_OPEN,
                    CommunicationEventType.EMAIL_CLICK
                ],
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported EMAIL_OPEN and EMAIL_CLICK events only")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_manifest_only_export():
    """Example 6: Export manifest only (metadata without full data files)"""
    print("\n=== Example 6: Manifest-Only Export ===")
    print("Export only manifest metadata without full event data files")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure for manifest only
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 90
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [],
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": None,
                "event_types": None,
                "manifest_only": True  # Only export manifest
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nManifest-only export completed successfully!")
        print(f"Downloaded manifest metadata without full event data")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_export_with_exclusions():
    """Example 7: Export with participant exclusions"""
    print("\n=== Example 7: Export with Participant Exclusions ===")
    print("Export events while excluding specific participants")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure with exclusions
        config_manager.update_config({
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 30
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890, 11111, 22222, 33333, 44444],
                "max_participants": None,
                "exclude_participant_ids": [22222, 44444],  # Exclude these
                "event_sources": None,
                "event_types": None,
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Create client and exporter
        client = VibrentHealthAPIClient(config_manager)
        exporter = CommunicationEventsExporter(client, config_manager)

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported events for 4 participants (2 excluded)")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def example_using_factory_pattern():
    """Example 8: Using ExporterFactory to create communication events exporter"""
    print("\n=== Example 8: Using Factory Pattern ===")
    print("Demonstrate using ExporterFactory for communication events exports")

    try:
        # Load configuration
        config_manager = ConfigManager()

        # Configure communication events export
        config_manager.update_config({
            "export": {
                "type": "communication_events"  # Factory will auto-create exporter
            },
            "communication_events_export": {
                "use_date_range": True,
                "date_range": {
                    "default_days_back": 7
                },
                "monitoring": {
                    "polling_interval": 10,
                    "max_wait_time": None,
                    "continue_on_failure": True
                },
                "participant_ids": [12345, 67890],
                "max_participants": None,
                "exclude_participant_ids": None,
                "event_sources": [CommunicationEventSource.ITERABLE],
                "event_types": [
                    CommunicationEventType.EMAIL_SENT,
                    CommunicationEventType.EMAIL_DELIVERY
                ],
                "manifest_only": False
            }
        })

        # Setup logging
        setup_logging()

        # Use factory to create the right exporter automatically
        from vibrent_api_client.core.exporter_factory import ExporterFactory

        client = VibrentHealthAPIClient(config_manager)
        export_type = config_manager.get("export.type", "survey")

        # Factory automatically creates CommunicationEventsExporter
        exporter = ExporterFactory.create_exporter(export_type, client, config_manager)

        print(f"Factory created: {exporter.__class__.__name__}")

        # Run export
        orchestrator = ExportOrchestrator(exporter, config_manager)
        metadata = orchestrator.run_export()

        print(f"\nExport completed successfully!")
        print(f"Exported ITERABLE email sent/delivery events for 2 participants")
        print(f"Output directory: {metadata.output_directory}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all examples"""
    print("=" * 80)
    print("Vibrent Health API Client - Communication Events Export Examples")
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
        # Example 1: Export all events
        # example_export_all_events()

        # Example 2: Specific participants with date range
        # example_export_specific_participants_with_date_range()

        # Example 3: Email events only
        # example_export_email_events_only()

        # Example 4: SMS events only
        # example_export_sms_events_only()

        # Example 5: Specific event types
        # example_export_specific_event_types()

        # Example 6: Manifest only
        # example_manifest_only_export()

        # Example 7: With exclusions
        # example_export_with_exclusions()

        # Example 8: Factory pattern
        example_using_factory_pattern()

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
