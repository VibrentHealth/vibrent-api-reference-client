#!/usr/bin/env python3
"""
Simple runner script for Vibrent Health API Client

This script makes it easy to run the export without dealing with module paths.
"""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the required modules
from vibrent_api_client.core.config import ConfigManager, ConfigurationError
from vibrent_api_client.core.exporter import SurveyDataExporter
from vibrent_api_client.utils.helpers import setup_logging


def main():
    """Main entry point"""
    load_dotenv()

    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)

        # Print license information
        print("Vibrent Health API Client - Reference Implementation")
        print("=" * 50)
        print("⚠️  IMPORTANT: This is a reference implementation only")
        print("   - Not intended for production use without testing")
        print("   - No active support or updates provided")
        print("   - No version compatibility guarantees")
        print("   - Report issues to info@vibrenthealth.com")
        print("   - Use at your own risk")
        print("=" * 50)

        # Initialize and run exporter
        environment = os.getenv("VIBRENT_ENVIRONMENT") or config_manager.get("environment.default")
        
        exporter = SurveyDataExporter(config_manager=config_manager, environment=environment)
        exporter.run_export()

    except ConfigurationError as e:
        print(f"Configuration error: {str(e)}")
        print("\nPlease make sure to:")
        print("1. Replace placeholder URLs in config/vibrent_config.yaml with your actual Vibrent Health API URLs")
        print("2. Set VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables")
        return 1
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
