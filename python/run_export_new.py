#!/usr/bin/env python3
"""
Export runner using the new extensible architecture

This script demonstrates using the new ExportOrchestrator with ExporterFactory
to support multiple export types.

Usage:
    # Survey export (default)
    python run_export_new.py

    # Specify export type
    python run_export_new.py --export-type survey

    # With custom config
    python run_export_new.py --config path/to/config.yaml
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the new architecture
from vibrent_api_client.core.config import ConfigManager, ConfigurationError
from vibrent_api_client.core.client import VibrentHealthAPIClient
from vibrent_api_client.core.exporter_factory import ExporterFactory
from vibrent_api_client.core.orchestrator import ExportOrchestrator
from vibrent_api_client.utils.helpers import setup_logging


def main():
    """Main entry point"""
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Vibrent Health API Client - Extensible Export System"
    )
    parser.add_argument(
        "config_file",
        nargs="?",
        help="Path to configuration file (optional)"
    )
    parser.add_argument(
        "--export-type",
        type=str,
        help="Export type (survey, survey_v2, ehr, etc.)"
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List available export types and exit"
    )
    args = parser.parse_args()

    try:
        # Load configuration
        config_manager = ConfigManager(config_file=args.config_file)

        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)

        # Print header
        print("Vibrent Health API Client - Extensible Export System (v2.0)")
        print("=" * 60)
        print("⚠️  IMPORTANT: This is a reference implementation only")
        print("   - Not intended for production use without testing")
        print("   - No active support or updates provided")
        print("   - No version compatibility guarantees")
        print("   - Report issues to info@vibrenthealth.com")
        print("   - Use at your own risk")
        print("=" * 60)

        # List available export types if requested
        if args.list_types:
            print("\nAvailable Export Types:")
            registered_types = ExporterFactory.get_registered_types()
            if registered_types:
                for export_type in registered_types:
                    print(f"  - {export_type}")
            else:
                print("  (No export types registered)")
            return 0

        # Get export type from CLI or config
        export_type = args.export_type or config_manager.get("export.type", "survey")

        # Check if export type is registered
        if not ExporterFactory.is_registered(export_type):
            available = ", ".join(ExporterFactory.get_registered_types())
            print(f"\nError: Unknown export type '{export_type}'")
            print(f"Available types: {available}")
            print("\nUse --list-types to see all available export types")
            return 1

        print(f"\nExport Type: {export_type}")
        print(f"Environment: {config_manager.get('environment.default')}")
        print()

        # Create API client
        environment = os.getenv("VIBRENT_ENVIRONMENT") or config_manager.get("environment.default")
        client = VibrentHealthAPIClient(config_manager, environment)

        # Create appropriate exporter using factory
        logger.info(f"Creating {export_type} exporter...")
        exporter = ExporterFactory.create_exporter(export_type, client, config_manager)

        # Create orchestrator and run export
        logger.info("Initializing export orchestrator...")
        orchestrator = ExportOrchestrator(exporter, config_manager)

        logger.info("Starting export process...")
        metadata = orchestrator.run_export()

        # Print summary
        print("\n" + "=" * 60)
        print("Export Complete!")
        print(f"  Total items: {metadata.total_surveys}")
        print(f"  Successful: {metadata.successful_exports}")
        print(f"  Failed: {metadata.failed_exports}")
        print(f"  Duration: {metadata.duration_seconds:.2f} seconds")
        print(f"  Output: {metadata.output_directory}")
        print("=" * 60)

        return 0

    except ConfigurationError as e:
        print(f"\nConfiguration error: {str(e)}")
        print("\nPlease make sure to:")
        print("1. Replace placeholder URLs in shared/config/vibrent_config.yaml")
        print("2. Set VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables")
        print("3. You can specify a custom config file: python run_export_new.py <path_to_config>")
        return 1
    except ValueError as e:
        print(f"\nError: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
