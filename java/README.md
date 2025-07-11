# Vibrent Health API Client - Java Implementation

This is the Java reference implementation for accessing Vibrent Health APIs. It provides the same functionality as the Python implementation but written in Java.


## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher
- Access to Vibrent Health APIs

## Quick Start

### 1. Build and Run the Project

**Option A: Using the unified script (recommended)**
```bash
# From the parent directory
./run_java_client.sh
```

**Option B: Manual build**
```bash
cd java
mvn clean package
```

Both approaches will create a shaded JAR file in `target/vibrent-api-client-1.0.0.jar`.

### 2. Configure Environment Variables

Set your Vibrent Health API credentials:

```bash
export VIBRENT_CLIENT_ID="your_client_id"
export VIBRENT_CLIENT_SECRET="your_client_secret"
export VIBRENT_ENVIRONMENT="staging"  # or "production"
```

Alternatively, create a `.env` file in the project root:

```env
VIBRENT_CLIENT_ID=your_client_id
VIBRENT_CLIENT_SECRET=your_client_secret
VIBRENT_ENVIRONMENT=staging
```

### 3. Update Configuration

Edit `shared/config/vibrent_config.yaml` and replace the placeholder URLs with your actual Vibrent Health API URLs.

### 4. Run the Export

```bash
# Option A: Using the unified script (recommended)
./run_java_client.sh

# Option B: Using the shaded JAR directly
java -jar target/vibrent-api-client-1.0.0.jar

# Option C: With custom config file
java -jar target/vibrent-api-client-1.0.0.jar path/to/custom/config.yaml

# Option D: Using Maven
mvn exec:java -Dexec.mainClass="com.vibrenthealth.apiclient.RunExport"
```

## Project Structure

```
java/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/vibrenthealth/apiclient/
│       │       ├── core/                    # Core functionality
│       │       │   ├── AuthenticationManager.java
│       │       │   ├── ConfigManager.java
│       │       │   ├── Constants.java
│       │       │   ├── SurveyDataExporter.java
│       │       │   └── VibrentHealthAPIClient.java
│       │       ├── models/                  # Data models
│       │       │   ├── ExportMetadata.java
│       │       │   ├── ExportRequest.java
│       │       │   ├── ExportStatus.java
│       │       │   └── Survey.java
│       │       ├── utils/                   # Utility functions
│       │       │   └── Helpers.java
│       │       └── RunExport.java           # Main entry point
│       └── resources/
│           └── logback.xml                  # Logging configuration
├── examples/
│   └── ConfiguredExport.java               # Usage example
├── pom.xml                                 # Maven configuration
└── README.md                               # This file
```

## Configuration

The Java implementation uses the same shared configuration files as the Python version:

- **Shared Config**: `shared/config/vibrent_config.yaml`
- **Environment Variables**: `VIBRENT_CLIENT_ID`, `VIBRENT_CLIENT_SECRET`, `VIBRENT_ENVIRONMENT`

### Configuration Structure

```yaml
environment:
  default: staging
  environments:
    staging:
      base_url: "YOUR_STAGING_BASE_URL_HERE"
      token_url: "YOUR_STAGING_TOKEN_URL_HERE"
    production:
      base_url: "YOUR_PRODUCTION_BASE_URL_HERE"
      token_url: "YOUR_PRODUCTION_TOKEN_URL_HERE"

auth:
  timeout: 30
  refresh_buffer: 300

api:
  timeout: 30

export:
  date_range:
    default_days_back: 30
    absolute_start_date: null
    absolute_end_date: null
  format: JSON
  request:
    max_surveys: null
    survey_ids: null
    exclude_survey_ids: null
  monitoring:
    polling_interval: 10
    max_wait_time: null
    continue_on_failure: true

output:
  base_directory: output
  survey_exports_dir: survey_exports
  extract_json: true
  remove_zip_after_extract: true

metadata:
  save_metadata: true
  filename: export_metadata.json
  include_survey_details: true
  include_export_status: true
```

## Usage Examples

### Basic Usage

```java
import com.vibrenthealth.apiclient.core.ConfigManager;
import com.vibrenthealth.apiclient.core.SurveyDataExporter;

// Load configuration
ConfigManager configManager = new ConfigManager();

// Create exporter
SurveyDataExporter exporter = new SurveyDataExporter(configManager, "staging", null);

// Run export
exporter.runExport();
```

### Custom Configuration

```java
// Load from specific config file
ConfigManager configManager = new ConfigManager("path/to/config.yaml");

// Use specific environment
SurveyDataExporter exporter = new SurveyDataExporter(configManager, "production", null);
```

### Programmatic Configuration

```java
// Create export request manually
ExportRequest request = new ExportRequest(
    System.currentTimeMillis() - (30 * 24 * 60 * 60 * 1000L), // 30 days ago
    System.currentTimeMillis(), // now
    "JSON"
);
```

## Output Structure

The Java implementation creates the same output structure as Python:

```
java/output/
├── survey_exports/
│   └── survey_data_DD_MM_YYYY_HHMMSS/
│       ├── export_metadata.json
│       ├── export_12345.zip
│       ├── export_67890.zip
│       ├── survey_data_12345.json
│       └── survey_data_67890.json
└── logs/
    └── vibrent-api-client.log
```

## Logging

The application uses SLF4J with Logback for logging. Logs are written to:

- **Console**: Standard output with INFO level and above
- **File**: `java/output/logs/vibrent-api-client.log` with rolling policy

### Log Levels

- `INFO`: General application flow
- `WARN`: Non-critical issues
- `ERROR`: Errors that may affect functionality
- `DEBUG`: Detailed debugging information

## Dependencies

The project uses modern, well-maintained libraries:

- **OkHttp 4.12.0**: HTTP client for API requests
- **Jackson 2.15.2**: JSON processing with JSR310 support
- **SnakeYAML 2.0**: YAML configuration parsing
- **SLF4J + Logback**: Logging framework
- **Apache Commons Compress 1.24.0**: ZIP file processing
- **dotenv-java 3.0.0**: Environment variable loading
- **Lombok 1.18.30**: Reduces boilerplate code for data models
- **JUnit 5.9.3 + Mockito 5.3.1**: Testing framework

## Building and Testing

### Build

```bash
mvn clean package
```

### Run Tests

```bash
mvn test
```

### Create Executable JAR

```bash
mvn clean package
# The shaded JAR will be created at: target/vibrent-api-client-1.0.0.jar
```

## Troubleshooting

### Common Issues

1. **Configuration not found**: Ensure `shared/config/vibrent_config.yaml` exists and is properly formatted
2. **Authentication failed**: Verify `VIBRENT_CLIENT_ID` and `VIBRENT_CLIENT_SECRET` are set correctly
3. **Network timeouts**: Check your internet connection and API endpoint URLs
4. **Permission errors**: Ensure the application has write permissions to the output directory

### Debug Mode

Enable debug logging by modifying `src/main/resources/logback.xml`:

```xml
<logger name="com.vibrenthealth.apiclient" level="DEBUG" />
```

## API Reference

### Core Classes

- **`ConfigManager`**: Configuration loading and management
- **`AuthenticationManager`**: OAuth2 authentication handling
- **`VibrentHealthAPIClient`**: Main API client for HTTP requests
- **`SurveyDataExporter`**: Orchestrates the complete export process

### Data Models

All data models use Lombok annotations to reduce boilerplate code:

- **`Survey`**: Represents a survey from the API
- **`ExportRequest`**: Export request parameters
- **`ExportStatus`**: Status of an export request
- **`ExportMetadata`**: Metadata for the export session

### Lombok Usage

The project uses Lombok to automatically generate:
- Getters and setters (`@Data`)
- Constructors (`@NoArgsConstructor`, `@AllArgsConstructor`)
- `equals()`, `hashCode()`, and `toString()` methods (`@Data`)

This significantly reduces boilerplate code while maintaining full functionality.

## License

This is a reference implementation provided by Vibrent Health. Please refer to the main project license for terms and conditions. 