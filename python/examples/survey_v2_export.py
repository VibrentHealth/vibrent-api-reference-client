#!/usr/bin/env python3
"""
Survey V2 Export Example

This script demonstrates how to use the Survey V2 exporter with wide format
reporting and advanced options like PII removal, custom choice formats, etc.

The V2 API provides:
- Wide format reporting (one row per participant)
- Data dictionary inclusion
- PII removal options
- Custom choice value formats
- User type filtering
- Completed-only or all responses

Usage:
    python examples/survey_v2_export.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from dotenv import load_dotenv

from vibrent_api_client import (
    ConfigManager,
    VibrentHealthAPIClient,
    SurveyV2Exporter,
    ExportOrchestrator
)


def example_basic_v2_export():
    """Example 1: Basic Survey V2 export with default settings"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Survey V2 Export (CSV, Wide Format)")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    # Create configuration
    config_manager = ConfigManager()

    # Override config to use Survey V2
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'survey_v2': {
                'file_type': 'CSV',
                'completed_only': True,
                'user_type': 'REAL_ONLY',
                'request': {
                    'max_surveys': 2  # Limit for demo
                }
            }
        }
    })

    # Create client and exporter
    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)

    # Run export via orchestrator
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Export Complete!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Output: {metadata.output_directory}")


def example_pii_removal():
    """Example 2: Survey V2 export with PII removal"""
    print("\n" + "=" * 60)
    print("Example 2: Survey V2 Export with PII Removal")
    print("=" * 60)

    load_dotenv()
    config_manager = ConfigManager()

    # Configure for PII removal
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'survey_v2': {
                'file_type': 'CSV',
                'remove_pii': True,  # Remove personally identifiable information
                'completed_only': True,
                'user_type': 'REAL_ONLY',
                'request': {
                    'max_surveys': 1
                }
            }
        }
    })

    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Export Complete with PII Removed!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Output: {metadata.output_directory}")


def example_custom_choice_format():
    """Example 3: Survey V2 export with custom choice value format"""
    print("\n" + "=" * 60)
    print("Example 3: Survey V2 Export with Custom Choice Format")
    print("=" * 60)

    load_dotenv()
    config_manager = ConfigManager()

    # Configure choice value format
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'survey_v2': {
                'file_type': 'CSV',
                'choice_value_format': 'TEXT_ONLY',  # TEXT_ONLY, VALUE_ONLY, VALUE_AND_TEXT
                'completed_only': True,
                'user_type': 'REAL_ONLY',
                'request': {
                    'max_surveys': 1
                }
            }
        }
    })

    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Export Complete with TEXT_ONLY choice format!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Output: {metadata.output_directory}")


def example_json_format():
    """Example 4: Survey V2 export in JSON format"""
    print("\n" + "=" * 60)
    print("Example 4: Survey V2 Export in JSON Format")
    print("=" * 60)

    load_dotenv()
    config_manager = ConfigManager()

    # Configure for JSON output
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'survey_v2': {
                'file_type': 'JSON',  # Export as JSON instead of CSV
                'completed_only': True,
                'user_type': 'REAL_ONLY',
                'request': {
                    'max_surveys': 1
                }
            }
        }
    })

    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Export Complete in JSON format!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Output: {metadata.output_directory}")


def example_all_users_including_test():
    """Example 5: Survey V2 export including test users"""
    print("\n" + "=" * 60)
    print("Example 5: Survey V2 Export Including Test Users")
    print("=" * 60)

    load_dotenv()
    config_manager = ConfigManager()

    # Configure to include all users (test + real)
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'survey_v2': {
                'file_type': 'CSV',
                'user_type': 'ALL_USERS',  # Include both real and test users
                'completed_only': False,  # Include incomplete responses too
                'include_withdrawn_user': True,  # Include withdrawn users
                'request': {
                    'max_surveys': 1
                }
            }
        }
    })

    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Export Complete including all users!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Output: {metadata.output_directory}")


def example_programmatic_configuration():
    """Example 6: Fully programmatic V2 export configuration"""
    print("\n" + "=" * 60)
    print("Example 6: Programmatic Survey V2 Export")
    print("=" * 60)

    load_dotenv()
    config_manager = ConfigManager()

    # Comprehensive V2 configuration
    config_manager.update_config({
        'export': {
            'type': 'survey_v2',
            'date_range': {
                'default_days_back': 7  # Last 7 days
            },
            'survey_v2': {
                'file_type': 'CSV',
                'remove_pii': False,
                'completed_only': True,
                'include_withdrawn_user': True,
                'combine_values_for_multiple_choices': True,
                'choice_value_format': 'VALUE_AND_TEXT',
                'user_type': 'REAL_ONLY',
                'request': {
                    'survey_ids': None,  # All surveys, or specify [1234, 5678]
                    'max_surveys': 3
                }
            }
        },
        'output': {
            'extract_files': True,
            'remove_zip_after_extract': True
        }
    })

    client = VibrentHealthAPIClient(config_manager)
    exporter = SurveyV2Exporter(client, config_manager)
    orchestrator = ExportOrchestrator(exporter, config_manager)
    metadata = orchestrator.run_export()

    print(f"\n✓ Programmatic export complete!")
    print(f"  Surveys exported: {metadata.successful_exports}")
    print(f"  Duration: {metadata.duration_seconds:.2f} seconds")
    print(f"  Output: {metadata.output_directory}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("Survey V2 Export Examples")
    print("Vibrent Health API Client - Reference Implementation")
    print("=" * 60)

    # Check for credentials
    if not os.getenv("VIBRENT_CLIENT_ID") or not os.getenv("VIBRENT_CLIENT_SECRET"):
        print("\n❌ Error: Missing credentials")
        print("Please set VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET")
        print("\nExample:")
        print("  export VIBRENT_CLIENT_ID='your_client_id'")
        print("  export VIBRENT_CLIENT_SECRET='your_client_secret'")
        return 1

    try:
        # Run examples (comment out the ones you don't want to run)
        example_basic_v2_export()
        # example_pii_removal()
        # example_custom_choice_format()
        # example_json_format()
        # example_all_users_including_test()
        # example_programmatic_configuration()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
