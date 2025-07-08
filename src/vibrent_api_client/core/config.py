"""
Configuration manager for Vibrent Health API Client

This module handles loading and managing configuration from YAML files
and environment variables.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import yaml

from .constants import (
    ConfigKeys, Environment, ErrorMessages,
    TimeConstants, ExportFormat, FileConstants
)


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


class ConfigManager:
    """Manages configuration for the Vibrent Health API Client"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Path to the YAML configuration file. If None, will look for
                        config/vibrent_config.yaml in the current directory
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file or self._find_config_file()
        self.config = self._load_config()
        self._validate_config()
    
    def _find_config_file(self) -> str:
        """Find the configuration file in common locations"""
        possible_paths = [
            "config/vibrent_config.yaml",
            "vibrent_config.yaml",
            "config.yaml",
            "config.yml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # If no config file found, create a default one
        default_config_path = "config/vibrent_config.yaml"
        self._create_default_config(default_config_path)
        return default_config_path
    
    def _create_default_config(self, config_path: str) -> None:
        """Create a default configuration file"""
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        default_config = {
            ConfigKeys.ENVIRONMENT: {
                ConfigKeys.DEFAULT: Environment.STAGING,
                ConfigKeys.ENVIRONMENTS: {
                    Environment.STAGING: {
                        ConfigKeys.BASE_URL: "YOUR_STAGING_BASE_URL_HERE",
                        ConfigKeys.TOKEN_URL: "YOUR_STAGING_TOKEN_URL_HERE"
                    },
                    Environment.PRODUCTION: {
                        ConfigKeys.BASE_URL: "YOUR_PRODUCTION_BASE_URL_HERE",
                        ConfigKeys.TOKEN_URL: "YOUR_PRODUCTION_TOKEN_URL_HERE"
                    }
                }
            },
            ConfigKeys.AUTH: {
                ConfigKeys.TIMEOUT: TimeConstants.DEFAULT_TIMEOUT,
                ConfigKeys.REFRESH_BUFFER: TimeConstants.TOKEN_REFRESH_BUFFER
            },
            ConfigKeys.API: {
                ConfigKeys.TIMEOUT: TimeConstants.DEFAULT_TIMEOUT
            },
            ConfigKeys.EXPORT: {
                ConfigKeys.DATE_RANGE: {
                    ConfigKeys.DEFAULT_DAYS_BACK: 30,
                    ConfigKeys.ABSOLUTE_START_DATE: None,
                    ConfigKeys.ABSOLUTE_END_DATE: None
                },
                ConfigKeys.FORMAT: ExportFormat.JSON,
                ConfigKeys.REQUEST: {
                    ConfigKeys.MAX_SURVEYS: None,
                    ConfigKeys.SURVEY_IDS: None,
                    ConfigKeys.EXCLUDE_SURVEY_IDS: None
                },
                ConfigKeys.MONITORING: {
                    ConfigKeys.POLLING_INTERVAL: TimeConstants.DEFAULT_POLLING_INTERVAL,
                    ConfigKeys.MAX_WAIT_TIME: None,
                    ConfigKeys.CONTINUE_ON_FAILURE: True
                }
            },
            ConfigKeys.OUTPUT: {
                ConfigKeys.BASE_DIRECTORY: FileConstants.OUTPUT_BASE_DIR,
                ConfigKeys.SURVEY_EXPORTS_DIR: FileConstants.SURVEY_EXPORTS_DIR,
                ConfigKeys.EXTRACT_JSON: True,
                ConfigKeys.REMOVE_ZIP_AFTER_EXTRACT: True
            },
            ConfigKeys.METADATA: {
                ConfigKeys.SAVE_METADATA: True,
                ConfigKeys.FILENAME: "export_metadata.json",
                ConfigKeys.INCLUDE_SURVEY_DETAILS: True,
                ConfigKeys.INCLUDE_EXPORT_STATUS: True
            }
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        self.logger.info(f"Created default configuration file: {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError("Configuration file is empty")
            
            self.logger.info(f"Loaded configuration from: {self.config_file}")
            return config
            
        except FileNotFoundError:
            raise ConfigurationError(
                ErrorMessages.CONFIG_FILE_NOT_FOUND.format(file_path=self.config_file)
            )
        except yaml.YAMLError as e:
            raise ConfigurationError(
                ErrorMessages.INVALID_CONFIG.format(error=str(e))
            )
        except Exception as e:
            raise ConfigurationError(
                ErrorMessages.INVALID_CONFIG.format(error=str(e))
            )
    
    def _validate_config(self) -> None:
        """Validate the loaded configuration"""
        required_sections = [
            ConfigKeys.ENVIRONMENT,
            ConfigKeys.AUTH,
            ConfigKeys.API,
            ConfigKeys.EXPORT,
            ConfigKeys.OUTPUT
        ]
        
        for section in required_sections:
            if section not in self.config:
                raise ConfigurationError(f"Missing required configuration section: {section}")
        
        # Validate environment configuration
        env_config = self.config[ConfigKeys.ENVIRONMENT]
        if ConfigKeys.DEFAULT not in env_config:
            raise ConfigurationError("Missing default environment configuration")
        
        default_env = env_config[ConfigKeys.DEFAULT]
        if default_env not in [Environment.STAGING, Environment.PRODUCTION]:
            raise ConfigurationError(f"Invalid default environment: {default_env}")
        
        if ConfigKeys.ENVIRONMENTS not in env_config:
            raise ConfigurationError("Missing environment-specific configurations")
        
        for env_name, env_settings in env_config[ConfigKeys.ENVIRONMENTS].items():
            if ConfigKeys.BASE_URL not in env_settings:
                raise ConfigurationError(f"Missing base_url for environment: {env_name}")
            if ConfigKeys.TOKEN_URL not in env_settings:
                raise ConfigurationError(f"Missing token_url for environment: {env_name}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation
        
        Args:
            key_path: Configuration key path (e.g., "environment.default")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_environment_config(self, environment: Optional[str] = None) -> Dict[str, str]:
        """
        Get configuration for a specific environment
        
        Args:
            environment: Environment name. If None, uses default environment
            
        Returns:
            Environment configuration dictionary
        """
        if environment is None:
            environment = self.get(f"{ConfigKeys.ENVIRONMENT}.{ConfigKeys.DEFAULT}")
        
        env_config = self.get(f"{ConfigKeys.ENVIRONMENT}.{ConfigKeys.ENVIRONMENTS}.{environment}")
        if not env_config:
            raise ConfigurationError(f"Environment configuration not found: {environment}")
        
        return env_config
    
    def get_date_range(self) -> Dict[str, int]:
        """
        Get the configured date range for exports
        
        Returns:
            Dictionary with start_time and end_time in milliseconds
        """
        date_config = self.get(f"{ConfigKeys.EXPORT}.{ConfigKeys.DATE_RANGE}")
        
        # Check for absolute dates first
        absolute_start = date_config.get(ConfigKeys.ABSOLUTE_START_DATE)
        absolute_end = date_config.get(ConfigKeys.ABSOLUTE_END_DATE)
        
        if absolute_start and absolute_end:
            # Convert ISO date strings to timestamps
            start_dt = datetime.fromisoformat(absolute_start)
            end_dt = datetime.fromisoformat(absolute_end)
            
            start_time = int(start_dt.timestamp() * 1000)
            end_time = int(end_dt.timestamp() * 1000)
        else:
            # Use relative date range
            days_back = date_config.get(ConfigKeys.DEFAULT_DAYS_BACK, 30)
            end_time = int(datetime.now().timestamp() * 1000)
            start_time = end_time - (days_back * TimeConstants.MS_PER_DAY)
        
        return {
            "start_time": start_time,
            "end_time": end_time
        }
    
    def get_survey_filter(self) -> Dict[str, Any]:
        """
        Get survey filtering configuration
        
        Returns:
            Dictionary with survey filtering settings
        """
        request_config = self.get(f"{ConfigKeys.EXPORT}.{ConfigKeys.REQUEST}")
        
        return {
            "max_surveys": request_config.get(ConfigKeys.MAX_SURVEYS),
            "survey_ids": request_config.get(ConfigKeys.SURVEY_IDS),
            "exclude_survey_ids": request_config.get(ConfigKeys.EXCLUDE_SURVEY_IDS)
        }
    
    def should_include_survey(self, survey_id: int, survey_name: str = "") -> bool:
        """
        Check if a survey should be included based on configuration
        
        Precedence order:
        1. survey_ids (inclusion) - if specified, only include these surveys
        2. exclude_survey_ids (exclusion) - if specified, exclude these surveys
        3. max_surveys - limit total number of surveys processed
        
        Args:
            survey_id: Survey ID
            survey_name: Survey name (for logging)
            
        Returns:
            True if survey should be included
        """
        filter_config = self.get_survey_filter()
        survey_ids = filter_config.get("survey_ids")
        exclude_survey_ids = filter_config.get("exclude_survey_ids")
        
        # Precedence 1: survey_ids (inclusion) takes highest priority
        if survey_ids is not None:
            if survey_id in survey_ids:
                self.logger.debug(f"Including survey {survey_id} ({survey_name}) - in survey_ids list")
                return True
            else:
                self.logger.debug(f"Skipping survey {survey_id} ({survey_name}) - not in survey_ids list")
                return False
        
        # Precedence 2: exclude_survey_ids (exclusion)
        if exclude_survey_ids is not None:
            if survey_id in exclude_survey_ids:
                self.logger.debug(f"Skipping survey {survey_id} ({survey_name}) - in exclude_survey_ids list")
                return False
        
        # If no inclusion/exclusion rules, include the survey
        self.logger.debug(f"Including survey {survey_id} ({survey_name}) - no filtering rules apply")
        return True
    

    
    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration
        
        Returns:
            Output configuration dictionary
        """
        return self.get(ConfigKeys.OUTPUT, {})
    
    def get_survey_output_directory(self) -> str:
        """
        Get the survey output directory path
        
        Returns:
            Full survey output directory path
        """
        output_config = self.get_output_config()
        base_dir = output_config.get(ConfigKeys.BASE_DIRECTORY, FileConstants.OUTPUT_BASE_DIR)
        survey_dir = output_config.get(ConfigKeys.SURVEY_EXPORTS_DIR, FileConstants.SURVEY_EXPORTS_DIR)
        
        # Return the full path
        return f"{base_dir}/{survey_dir}"
    
    def get_metadata_config(self) -> Dict[str, Any]:
        """
        Get metadata configuration
        
        Returns:
            Metadata configuration dictionary
        """
        return self.get(ConfigKeys.METADATA, {})
    

    
    def reload(self) -> None:
        """Reload configuration from file"""
        self.config = self._load_config()
        self._validate_config()
        self.logger.info("Configuration reloaded successfully")
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with new values
        
        Args:
            updates: Dictionary of configuration updates
        """
        def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
        self._validate_config()
        self.logger.info("Configuration updated successfully")
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """
        Save current configuration to file
        
        Args:
            file_path: Path to save configuration. If None, saves to original file
        """
        save_path = file_path or self.config_file
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to: {save_path}")
            
        except Exception as e:
            raise ConfigurationError(
                ErrorMessages.FILE_WRITE_ERROR.format(file_path=save_path, error=str(e))
            ) 