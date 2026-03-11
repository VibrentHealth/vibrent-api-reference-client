# Vibrent Health API Client

A reference implementation for accessing Vibrent Health APIs with comprehensive configuration support.

Vibrent Health maintains this repository to provide a demonstration implementation on the use of the Vibrent Health system integration. We expect that partners and users of this system may modify and maintain the use of this code in concordance with their own institution's policies.

## Quick Start

### Python Implementation

1. **Set environment variables**:
   ```bash
   export VIBRENT_CLIENT_ID="your_client_id"
   export VIBRENT_CLIENT_SECRET="your_client_secret"
   export VIBRENT_ENVIRONMENT="staging"  # or "production"
   ```

2. **Configure the client** (required):
   The client will automatically create a default configuration file at `shared/config/vibrent_config.yaml` if none exists. You must customize this file to:
   - Replace placeholder URLs with your actual Vibrent Health API URLs
   - Set date ranges (relative or absolute)
   - Filter specific surveys
   - Configure logging options
   - Set export parameters
   
   See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

3. **Setup and run**:
   ```bash
   # Option 1: Setup and run in one command (recommended)
   ./run_python_client.sh
   
   # Option 2: Setup only
   ./run_python_client.sh --setup
   
   # Option 3: Run only (if already set up)
   ./run_python_client.sh --run
   
   # Option 4: Manual setup and run
   cd python
   pip install -r requirements.txt
   python run_export_new.py
   ```


## Key Features

- **Flexible Date Ranges**: Support for both relative (days back) and absolute date ranges
- **Automatic Date Range Splitting**: Large date ranges (>6 months) are automatically split into smaller chunks for better API performance
- **Survey Filtering**: Export specific surveys by ID, exclude specific surveys, or limit the number of surveys processed
- **File Merging**: Multiple export files for the same survey are automatically merged into a single file
- **Organized Output Structure**: Hierarchical output directories with clear file naming conventions
- **Environment Configuration**: All API endpoints and authentication URLs are configurable
- **Error Handling**: Configurable error reporting
- **Metadata Export**: Detailed export metadata with survey and status information
- **UTC Timezone Support**: All timestamps use UTC for consistent behavior across different timezones

## Usage as Python Module

```python
import sys
sys.path.append('src')

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.exporter import SurveyDataExporter

# Load configuration
config_manager = ConfigManager()

# Initialize exporter with configuration
exporter = SurveyDataExporter(config_manager=config_manager, environment="staging")

# Run export (uses configuration for date range and survey filtering)
exporter.run_export()
```

## Configuration

The client uses a YAML-based configuration system that allows you to customize all aspects of the export process. Key configuration options include:

- **Date Ranges**: Relative (`default_days_back: 30`) or absolute (`absolute_start_date: "2024-01-01"`)
- **Survey Filtering**: 
  - Include specific surveys: `survey_ids: [123, 456, 789]`
  - Exclude specific surveys: `exclude_survey_ids: [999, 888, 777]`
  - Limit total surveys: `max_surveys: 10`
- **Export Options**: Format, monitoring intervals

See [CONFIGURATION.md](CONFIGURATION.md) for complete documentation.

## Environment Variables

- `VIBRENT_CLIENT_ID`: Your Vibrent Health client ID
- `VIBRENT_CLIENT_SECRET`: Your Vibrent Health client secret
- `VIBRENT_ENVIRONMENT`: Environment to use ("staging", "production")

**Note**: The `VIBRENT_EXPORT_DAYS` environment variable is deprecated. Use the configuration file instead.

## License

This project is licensed under the MIT License with additional disclaimers. See [LICENSE](LICENSE) file for complete terms and conditions.

## Support and Issues

- **No Technical Support**: Vibrent Health does not provide technical support for this reference implementation
- **Issue Reporting**: Report bugs or issues to info@vibrenthealth.com for review
- **No Updates**: This reference implementation is not actively maintained or updated
- **Use at Your Own Risk**: Users are responsible for their own implementation, testing, and deployment 

---

## Structure

This repository is organized to support multiple language implementations:

- `python/` – Python reference implementation (see `python/README.md`)
- `javascript/` – (planned) JavaScript/Node.js implementation

Each language implementation writes its output to its own subfolder (e.g., `python/output/`).

## Configuration

All implementations share the same configuration files in `shared/config/`:
- `shared/config/vibrent_config.yaml` - Main configuration file
- `shared/config/sample_config.yaml` - Sample configuration template