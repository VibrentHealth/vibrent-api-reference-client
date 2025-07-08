# Vibrent Health API Client Configuration Guide

This document explains how to configure the Vibrent Health API Client using the new YAML-based configuration system.

## Overview

The Vibrent Health API Client now uses a comprehensive configuration system that allows you to customize all aspects of the export process without modifying the code. The configuration is stored in YAML files and supports both relative and absolute date ranges, survey filtering, and extensive logging options.

## Configuration File Location

The client will look for configuration files in the following order:
1. `config/vibrent_config.yaml` (recommended)
2. `vibrent_config.yaml`
3. `config.yaml`
4. `config.yml`

If no configuration file is found, a default configuration will be created at `config/vibrent_config.yaml`.

## Key Features

### 1. Date Range Configuration

The client now supports both relative and absolute date ranges:

#### Relative Date Range (Default)
```yaml
export:
  date_range:
    default_days_back: 30  # Export data from last 30 days
```

#### Absolute Date Range
```yaml
export:
  date_range:
    absolute_start_date: "2024-01-01"  # Start date in ISO format
    absolute_end_date: "2024-12-31"    # End date in ISO format
```

**Note**: If both absolute dates are specified, they will override the relative date range.

### 2. Survey Filtering

You can now specify which surveys to export with three levels of filtering:

```yaml
export:
  request:
    # Export only specific survey IDs (highest precedence)
    survey_ids: [123, 456, 789]
    
    # Exclude specific survey IDs (ignored if survey_ids is specified)
    exclude_survey_ids: [999, 888, 777]
    
    # Maximum number of surveys to process (lowest precedence)
    max_surveys: 10
```

**Precedence Order:**
1. **survey_ids** (inclusion) - If specified, only these surveys will be exported
2. **exclude_survey_ids** (exclusion) - If specified, these surveys will be excluded (ignored if survey_ids is specified)
3. **max_surveys** - Limits the total number of surveys processed



### 4. Environment Configuration

All environment-specific URLs are configurable. You must replace the placeholder URLs with your actual Vibrent Health API URLs:

```yaml
environment:
  default: "staging"
  environments:
    staging:
      base_url: "YOUR_STAGING_BASE_URL_HERE"
      token_url: "YOUR_STAGING_TOKEN_URL_HERE"
    production:
      base_url: "YOUR_PRODUCTION_BASE_URL_HERE"
      token_url: "YOUR_PRODUCTION_TOKEN_URL_HERE"
```

## Configuration Sections

### Environment Configuration
- **default**: Default environment to use
- **environments**: Environment-specific settings (base_url, token_url)

### Authentication Configuration
- **timeout**: Request timeout in seconds
- **refresh_buffer**: Token refresh buffer time in seconds

### API Configuration
- **timeout**: API request timeout

### Export Configuration
- **date_range**: Date range settings (relative or absolute)
- **format**: Export format (JSON, CSV)
- **request**: Survey filtering and processing limits
- **monitoring**: Export monitoring settings

### Output Configuration
- **base_directory**: Base directory for all exports (default: "output")
- **survey_exports_dir**: Survey exports directory under base_directory (default: "survey_exports")
- **extract_json**: Whether to extract JSON files from zip archives
- **remove_zip_after_extract**: Whether to remove zip files after extraction





### Metadata Configuration
- **save_metadata**: Whether to save export metadata
- **filename**: Metadata file name
- **include_survey_details**: Whether to include survey details in metadata
- **include_export_status**: Whether to include export status details

## Usage Examples

### Example 1: Export Specific Surveys for a Date Range

```yaml
export:
  date_range:
    absolute_start_date: "2024-01-01"
    absolute_end_date: "2024-01-31"
  request:
    survey_ids: [123, 456, 789]
```

### Example 2: Export All Surveys from Last 7 Days

```yaml
export:
  date_range:
    default_days_back: 7
  request:
    survey_ids: null  # Export all surveys
```

### Example 3: Export All Surveys Except Specific Ones

```yaml
export:
  date_range:
    default_days_back: 30
  request:
    survey_ids: null  # Export all surveys
    exclude_survey_ids: [999, 888, 777]  # Exclude these specific surveys
    max_surveys: 50  # Limit to 50 surveys
```



### Example 4: Production Environment

```yaml
environment:
  default: "production"
  environments:
    production:
      base_url: "https://your-production-api.vibrenthealth.com"
      token_url: "https://your-production-auth.vibrenthealth.com/token"

export:
  monitoring:
    polling_interval: 5
    max_wait_time: 3600  # 1 hour
    continue_on_failure: false
```

### Example 5: Custom Output Structure

```yaml
output:
  base_directory: "vibrent_data"
  survey_exports_dir: "survey_data"
  extract_json: true
  remove_zip_after_extract: false
```

This creates the following directory structure:
```
vibrent_data/
└── survey_data/
    └── survey_data_25_12_2024_143022/
```

## Environment Variables

The following environment variables are still supported and will override configuration settings:

- `VIBRENT_CLIENT_ID`: Your client ID
- `VIBRENT_CLIENT_SECRET`: Your client secret
- `VIBRENT_ENVIRONMENT`: Environment to use (staging, production)

## Migration from Previous Version

If you're upgrading from a previous version:

1. The client will automatically create a default configuration file if none exists
2. All hardcoded values are now configurable
3. The `days_back` parameter is now configured in the YAML file
4. Survey filtering is now available through configuration
5. Logging includes survey names by default

## Troubleshooting

### Configuration File Not Found
If you get a "Configuration file not found" error, the client will create a default configuration file. Check the `config/` directory for the new file.

### Invalid Configuration
If you get an "Invalid configuration" error, check:
1. YAML syntax is correct
2. All required sections are present
3. Environment URLs are properly configured (replace placeholder URLs with actual URLs)

### Date Range Issues
- Ensure absolute dates are in ISO format (YYYY-MM-DD)
- Relative dates use `default_days_back` parameter
- Only one date range method should be active at a time

## Sample Configuration

See `config/sample_config.yaml` for a complete example of all available configuration options. 