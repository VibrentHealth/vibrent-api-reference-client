#!/usr/bin/env python3
"""
Example script demonstrating the new configuration system for Vibrent Health API Client

This script shows how to:
1. Load and customize configuration
2. Use different date range options
3. Filter surveys
4. Configure logging
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from vibrent_api_client.core.config import ConfigManager, ConfigurationError
from vibrent_api_client.core.exporter import SurveyDataExporter
from vibrent_api_client.utils.helpers import setup_logging_from_config


def example_relative_date_range():
    """Example: Export data from last 7 days"""
    print("\n=== Example 1: Relative Date Range (Last 7 Days) ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Update configuration for this example
        config_manager.update_config({
            "export": {
                "date_range": {
                    "default_days_back": 7,
                    "absolute_start_date": None,
                    "absolute_end_date": None
                },
                "request": {
                    "max_surveys": 3,  # Limit to 3 surveys for demo
                    "survey_ids": None
                }
            }
        })
        
        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)
        
        # Run export
        exporter = SurveyDataExporter(config_manager=config_manager)
        exporter.run_export()
        
    except Exception as e:
        print(f"Error: {e}")


def example_absolute_date_range():
    """Example: Export data for specific date range"""
    print("\n=== Example 2: Absolute Date Range (January 2024) ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Update configuration for this example
        config_manager.update_config({
            "export": {
                "date_range": {
                    "default_days_back": 30,
                    "absolute_start_date": "2024-01-01",
                    "absolute_end_date": "2024-01-31"
                },
                "request": {
                    "max_surveys": 2,  # Limit to 2 surveys for demo
                    "survey_ids": None
                }
            },
            "logging": {
                "level": "DEBUG",
                "survey": {
                    "include_names": True,
                    "format": "[{index}/{total}] Processing: {name} (ID: {id})"
                }
            }
        })
        
        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)
        
        # Run export
        exporter = SurveyDataExporter(config_manager=config_manager)
        exporter.run_export()
        
    except Exception as e:
        print(f"Error: {e}")


def example_survey_filtering():
    """Example: Export specific surveys only"""
    print("\n=== Example 3: Survey Filtering (Specific Survey IDs) ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Update configuration for this example
        config_manager.update_config({
            "export": {
                "date_range": {
                    "default_days_back": 30,
                    "absolute_start_date": None,
                    "absolute_end_date": None
                },
                "request": {
                    "max_surveys": None,
                    "survey_ids": [1, 2, 3]  # Only export these survey IDs
                }
            },
            "logging": {
                "level": "INFO",
                "survey": {
                    "include_names": True,
                    "format": "Exporting: {name} (ID: {id})"
                }
            }
        })
        
        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)
        
        # Run export
        exporter = SurveyDataExporter(config_manager=config_manager)
        exporter.run_export()
        
    except Exception as e:
        print(f"Error: {e}")


def example_survey_exclusion():
    """Example: Export all surveys except specific ones"""
    print("\n=== Example 4: Survey Exclusion (Exclude Specific Survey IDs) ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Update configuration for this example
        config_manager.update_config({
            "export": {
                "date_range": {
                    "default_days_back": 30,
                    "absolute_start_date": None,
                    "absolute_end_date": None
                },
                "request": {
                    "max_surveys": 10,  # Limit to 10 surveys
                    "survey_ids": None,  # Export all surveys (except excluded ones)
                    "exclude_survey_ids": [999, 888, 777]  # Exclude these survey IDs
                }
            },
            "logging": {
                "level": "INFO",
                "survey": {
                    "include_names": True,
                    "format": "Processing: {name} (ID: {id})"
                }
            }
        })
        
        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)
        
        # Run export
        exporter = SurveyDataExporter(config_manager=config_manager)
        exporter.run_export()
        
    except Exception as e:
        print(f"Error: {e}")


def example_custom_output():
    """Example: Custom output configuration"""
    print("\n=== Example 5: Custom Output Configuration ===")
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        
        # Update configuration for this example
        config_manager.update_config({
            "output": {
                "base_directory": "custom_exports",
                "survey_exports_dir": "survey_data",
                "extract_json": True,
                "remove_zip_after_extract": False  # Keep zip files
            },
            "export": {
                "date_range": {
                    "default_days_back": 1,  # Just 1 day for demo
                },
                "request": {
                    "max_surveys": 1,  # Just 1 survey for demo
                }
            },
            "metadata": {
                "save_metadata": True,
                "filename": "custom_metadata.json",
                "include_survey_details": True,
                "include_export_status": True
            }
        })
        
        # Setup logging
        logging_config = config_manager.get_logging_config()
        setup_logging_from_config(logging_config)
        
        # Run export
        exporter = SurveyDataExporter(config_manager=config_manager)
        exporter.run_export()
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main function to run examples"""
    print("Vibrent Health API Client - Configuration Examples")
    print("=" * 60)
    
    # Check if environment variables are set
    if not os.getenv("VIBRENT_CLIENT_ID") or not os.getenv("VIBRENT_CLIENT_SECRET"):
        print("Error: Please set VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables")
        print("Example:")
        print("  export VIBRENT_CLIENT_ID='your_client_id'")
        print("  export VIBRENT_CLIENT_SECRET='your_client_secret'")
        return 1
    
    try:
        # Run examples
        example_relative_date_range()
        example_absolute_date_range()
        example_survey_filtering()
        example_survey_exclusion()
        example_custom_output()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("Check the output directories for exported data and metadata files.")
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 