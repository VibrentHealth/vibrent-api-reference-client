#!/usr/bin/env python3
"""
Main entry point for Vibrent Health API Client

This module provides the command-line interface for the Vibrent Health API Client.
"""

import logging
import os

from dotenv import load_dotenv

from .core.config import ConfigManager, ConfigurationError
from .core.exporter import SurveyDataExporter
from .utils.helpers import setup_logging

# MIT License
LICENSE = """
MIT License

Copyright (c) 2025 Vibrent Health API Reference Implementation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

DISCLAIMER:
This code is provided for reference purposes only and is not officially 
maintained by Vibrent Health. For issues or updates, please contact 
Vibrent Health support at info@vibrenthealth.com.
"""


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
        return 1
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main()) 