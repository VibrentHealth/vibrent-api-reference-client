"""
Constants for Vibrent Health API Client

This module contains all the API endpoints, status codes, and other constants
used throughout the application.
"""

# API Endpoints
class APIEndpoints:
    """API endpoint constants"""
    
    # Survey endpoints
    SURVEYS = "/api/ext/forms"
    
    # Export endpoints
    EXPORT_REQUEST = "/api/ext/export/survey/{survey_id}/request"
    EXPORT_STATUS = "/api/ext/export/status/{export_id}"
    EXPORT_DOWNLOAD = "/api/ext/export/download/{export_id}"

# Export Status Constants
class ExportStatus:
    """Export status constants"""
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# Export Format Constants
class ExportFormat:
    """Export format constants"""
    JSON = "JSON"
    CSV = "CSV"

# Environment Constants
class Environment:
    """Environment constants"""
    STAGING = "staging"
    PRODUCTION = "production"

# Request Headers
class Headers:
    """Request header constants"""
    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"
    
    # Content types
    APPLICATION_X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"

# Time Constants
class TimeConstants:
    """Time-related constants"""
    # Milliseconds in a day
    MS_PER_DAY = 24 * 60 * 60 * 1000
    
    # Default timeouts
    DEFAULT_TIMEOUT = 30
    DEFAULT_POLLING_INTERVAL = 10
    
    # Token refresh buffer (5 minutes)
    TOKEN_REFRESH_BUFFER = 300

# File Constants
class FileConstants:
    """File-related constants"""
    # File extensions
    JSON_EXTENSION = ".json"
    
    # Default file patterns
    DEFAULT_METADATA_FILENAME = "export_metadata.json"
    
    # Output directory structure
    OUTPUT_BASE_DIR = "output"
    SURVEY_EXPORTS_DIR = "survey_exports"



# Error Messages
class ErrorMessages:
    """Error message constants"""
    # Authentication errors
    MISSING_CREDENTIALS = "VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables must be set"
    INVALID_ENVIRONMENT = "Invalid environment: {environment}"
    AUTHENTICATION_FAILED = "Authentication failed: {error}"
    
    # API errors
    API_REQUEST_FAILED = "API request failed: {error}"
    
    # Export errors
    NO_SURVEYS_FOUND = "No surveys found"
    EXPORT_REQUEST_FAILED = "Failed to request export for survey {survey_id}: {error}"
    EXPORT_DOWNLOAD_FAILED = "Failed to download export {export_id}: {error}"
    
    # Configuration errors
    CONFIG_FILE_NOT_FOUND = "Configuration file not found: {file_path}"
    INVALID_CONFIG = "Invalid configuration: {error}"
    
    # File errors
    FILE_WRITE_ERROR = "Failed to write file {file_path}: {error}"

# Success Messages
class SuccessMessages:
    """Success message constants"""
    AUTHENTICATION_SUCCESSFUL = "Authentication successful"
    EXPORT_COMPLETED = "Export completed successfully!"
    METADATA_SAVED = "Export metadata saved to: {file_path}"

# Configuration Keys
class ConfigKeys:
    """Configuration key constants"""
    # Top-level keys
    ENVIRONMENT = "environment"
    AUTH = "auth"
    API = "api"
    EXPORT = "export"
    OUTPUT = "output"
    LOGGING = "logging"
    METADATA = "metadata"
    
    # Environment keys
    DEFAULT = "default"
    ENVIRONMENTS = "environments"
    BASE_URL = "base_url"
    TOKEN_URL = "token_url"
    
    # Auth keys
    TIMEOUT = "timeout"
    REFRESH_BUFFER = "refresh_buffer"
    
    # Export keys
    DATE_RANGE = "date_range"
    FORMAT = "format"
    REQUEST = "request"
    MONITORING = "monitoring"
    
    # Date range keys
    DEFAULT_DAYS_BACK = "default_days_back"
    ABSOLUTE_START_DATE = "absolute_start_date"
    ABSOLUTE_END_DATE = "absolute_end_date"
    
    # Request keys
    MAX_SURVEYS = "max_surveys"
    SURVEY_IDS = "survey_ids"
    EXCLUDE_SURVEY_IDS = "exclude_survey_ids"
    
    # Monitoring keys
    POLLING_INTERVAL = "polling_interval"
    MAX_WAIT_TIME = "max_wait_time"
    CONTINUE_ON_FAILURE = "continue_on_failure"
    
    # Output keys
    BASE_DIRECTORY = "base_directory"
    SURVEY_EXPORTS_DIR = "survey_exports_dir"
    EXTRACT_JSON = "extract_json"
    REMOVE_ZIP_AFTER_EXTRACT = "remove_zip_after_extract"
    

    
    # Metadata keys
    SAVE_METADATA = "save_metadata"
    FILENAME = "filename"
    INCLUDE_SURVEY_DETAILS = "include_survey_details"
    INCLUDE_EXPORT_STATUS = "include_export_status" 