# Vibrent Health API Client

A reference implementation for accessing Vibrent Health APIs with comprehensive configuration support.

## ⚠️ Important Disclaimers

**This software is provided for reference purposes only with the following important limitations:**

1. **Reference Purpose Only**: This is a fully executable Python utility created primarily for reference purposes only. It demonstrates how to integrate with the Vibrent Health API but is not intended for production use without proper testing and customization.

2. **No Active Support**: Vibrent Health will not provide active updates, maintenance, or ongoing support for this reference implementation.

3. **No Version Compatibility**: Vibrent Health will not maintain version compatibility or provide backward compatibility guarantees when the underlying API or this reference implementation changes.

4. **Issue Reporting**: Any issues found with the code, logic, or implementation should be reported to info@vibrenthealth.com for review and potential future improvements.

5. **No Technical Support**: Vibrent Health will not be responsible for providing technical assistance, support, or guidance to users of this repository. Users are responsible for their own implementation, testing, and deployment.

**By using this software, you acknowledge and accept these limitations.**

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export VIBRENT_CLIENT_ID="your_client_id"
   export VIBRENT_CLIENT_SECRET="your_client_secret"
   export VIBRENT_ENVIRONMENT="staging"  # or "production"
   ```

3. **Configure the client** (required):
   The client will automatically create a default configuration file at `config/vibrent_config.yaml` if none exists. You must customize this file to:
   - Replace placeholder URLs with your actual Vibrent Health API URLs
   - Set date ranges (relative or absolute)
   - Filter specific surveys
   - Configure logging options
   - Set export parameters
   
   See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

4. **Run the export**:
   ```bash
   # Option 1: Using the simple runner script
   python run_export.py
   
   # Option 2: Direct module execution
   python src/vibrent_api_client/__main__.py
   ```

## Key Features

- **Flexible Date Ranges**: Support for both relative (days back) and absolute date ranges
- **Survey Filtering**: Export specific surveys by ID, exclude specific surveys, or limit the number of surveys processed
- **Organized Output Structure**: Hierarchical output directories for different data types
- **Environment Configuration**: All API endpoints and authentication URLs are configurable
- **Error Handling**: Configurable error reporting
- **Metadata Export**: Detailed export metadata with survey and status information

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

## Multi-language Structure

This repository is organized to support multiple language implementations:

- `python/` – Python reference implementation (see `python/README.md`)
- `javascript/` – (planned) JavaScript/Node.js implementation
- `java/` – (planned) Java implementation

Each language implementation writes its output to its own subfolder (e.g., `python/output/`).

## Configuration

All language implementations share the same configuration files in `shared/config/`:
- `shared/config/vibrent_config.yaml` - Main configuration file
- `shared/config/sample_config.yaml` - Sample configuration template

This ensures consistent behavior across all language implementations. 