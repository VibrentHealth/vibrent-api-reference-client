package com.vibrenthealth.apiclient.core;

/**
 * Constants for Vibrent Health API Client
 * 
 * This class contains all the API endpoints, status codes, and other constants
 * used throughout the application.
 */
public class Constants {
    
    // API Endpoints
    public static class APIEndpoints {
        /** API endpoint constants */
        
        // Survey endpoints
        public static final String SURVEYS = "/api/ext/forms";
        
        // Export endpoints
        public static final String EXPORT_REQUEST = "/api/ext/export/survey/{survey_id}/request";
        public static final String EXPORT_STATUS = "/api/ext/export/status/{export_id}";
        public static final String EXPORT_DOWNLOAD = "/api/ext/export/download/{export_id}";
    }
    
    // Export Status Constants
    public static class ExportStatus {
        /** Export status constants */
        public static final String SUBMITTED = "SUBMITTED";
        public static final String IN_PROGRESS = "IN_PROGRESS";
        public static final String COMPLETED = "COMPLETED";
        public static final String FAILED = "FAILED";
    }
    
    // Export Format Constants
    public static class ExportFormat {
        /** Export format constants */
        public static final String JSON = "JSON";
        public static final String CSV = "CSV";
    }
    
    // Environment Constants
    public static class Environment {
        /** Environment constants */
        public static final String STAGING = "staging";
        public static final String PRODUCTION = "production";
    }
    
    // Request Headers
    public static class Headers {
        /** Request header constants */
        public static final String AUTHORIZATION = "Authorization";
        public static final String CONTENT_TYPE = "Content-Type";
        
        // Content types
        public static final String APPLICATION_X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded";
    }
    
    // Time Constants
    public static class TimeConstants {
        /** Time-related constants */
        // Milliseconds in a day
        public static final long MS_PER_DAY = 24 * 60 * 60 * 1000L;
        
        // Default timeouts
        public static final int DEFAULT_TIMEOUT = 30;
        public static final int DEFAULT_POLLING_INTERVAL = 10;
        
        // Token refresh buffer (5 minutes)
        public static final int TOKEN_REFRESH_BUFFER = 300;
    }
    
    // File Constants
    public static class FileConstants {
        /** File-related constants */
        // File extensions
        public static final String JSON_EXTENSION = ".json";
        
        // Default file patterns
        public static final String DEFAULT_METADATA_FILENAME = "export_metadata.json";
        
        // Output directory structure
        public static final String OUTPUT_BASE_DIR = "output";
        public static final String SURVEY_EXPORTS_DIR = "survey_exports";
    }
    
    // Error Messages
    public static class ErrorMessages {
        /** Error message constants */
        // Authentication errors
        public static final String MISSING_CREDENTIALS = "VIBRENT_CLIENT_ID and VIBRENT_CLIENT_SECRET environment variables must be set";
        public static final String INVALID_ENVIRONMENT = "Invalid environment: %s";
        public static final String AUTHENTICATION_FAILED = "Authentication failed: %s";
        
        // API errors
        public static final String API_REQUEST_FAILED = "API request failed: %s";
        
        // Export errors
        public static final String NO_SURVEYS_FOUND = "No surveys found";
        public static final String EXPORT_REQUEST_FAILED = "Failed to request export for survey %d: %s";
        public static final String EXPORT_DOWNLOAD_FAILED = "Failed to download export %s: %s";
        
        // Configuration errors
        public static final String CONFIG_FILE_NOT_FOUND = "Configuration file not found: %s";
        public static final String INVALID_CONFIG = "Invalid configuration: %s";
        
        // File errors
        public static final String FILE_WRITE_ERROR = "Failed to write file %s: %s";
    }
    
    // Success Messages
    public static class SuccessMessages {
        /** Success message constants */
        public static final String AUTHENTICATION_SUCCESSFUL = "Authentication successful";
        public static final String EXPORT_COMPLETED = "Export completed successfully!";
        public static final String METADATA_SAVED = "Export metadata saved to: %s";
    }
    
    // Configuration Keys
    public static class ConfigKeys {
        /** Configuration key constants */
        // Top-level keys
        public static final String ENVIRONMENT = "environment";
        public static final String AUTH = "auth";
        public static final String API = "api";
        public static final String EXPORT = "export";
        public static final String OUTPUT = "output";
        public static final String LOGGING = "logging";
        public static final String METADATA = "metadata";
        
        // Environment keys
        public static final String DEFAULT = "default";
        public static final String ENVIRONMENTS = "environments";
        public static final String BASE_URL = "base_url";
        public static final String TOKEN_URL = "token_url";
        
        // Auth keys
        public static final String TIMEOUT = "timeout";
        public static final String REFRESH_BUFFER = "refresh_buffer";
        
        // Export keys
        public static final String DATE_RANGE = "date_range";
        public static final String FORMAT = "format";
        public static final String REQUEST = "request";
        public static final String MONITORING = "monitoring";
        
        // Date range keys
        public static final String DEFAULT_DAYS_BACK = "default_days_back";
        public static final String ABSOLUTE_START_DATE = "absolute_start_date";
        public static final String ABSOLUTE_END_DATE = "absolute_end_date";
        
        // Request keys
        public static final String MAX_SURVEYS = "max_surveys";
        public static final String SURVEY_IDS = "survey_ids";
        public static final String EXCLUDE_SURVEY_IDS = "exclude_survey_ids";
        
        // Monitoring keys
        public static final String POLLING_INTERVAL = "polling_interval";
        public static final String MAX_WAIT_TIME = "max_wait_time";
        public static final String CONTINUE_ON_FAILURE = "continue_on_failure";
        
        // Output keys
        public static final String BASE_DIRECTORY = "base_directory";
        public static final String SURVEY_EXPORTS_DIR = "survey_exports_dir";
        public static final String EXTRACT_JSON = "extract_json";
        public static final String REMOVE_ZIP_AFTER_EXTRACT = "remove_zip_after_extract";
        
        // Metadata keys
        public static final String SAVE_METADATA = "save_metadata";
        public static final String FILENAME = "filename";
        public static final String INCLUDE_SURVEY_DETAILS = "include_survey_details";
        public static final String INCLUDE_EXPORT_STATUS = "include_export_status";
    }
} 