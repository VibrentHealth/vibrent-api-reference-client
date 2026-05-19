# Vibrent Health API Client - Java Implementation

A config-driven client for exporting data from Vibrent Health APIs. Configure `vibrent_config.yaml`, set credentials, and run — the client handles authentication, form listing, export submission, polling, and download automatically.

## Prerequisites

- Java 11 or higher
- Maven 3.6 or higher
- Access to Vibrent Health APIs (client ID and secret)

## Quick Start

### 1. Build

```bash
# From the repository root (recommended)
./run_java_client.sh --build

# Or manually
cd java && mvn clean package
```

### 2. Configure

```bash
# Set credentials
export VIBRENT_CLIENT_ID="your_client_id"
export VIBRENT_CLIENT_SECRET="your_client_secret"
export VIBRENT_ENVIRONMENT="staging"   # or "production"

# Copy and edit config
cp shared/config/sample_config.yaml shared/config/vibrent_config.yaml
# Edit vibrent_config.yaml — set your API URLs and export options
```

### 3. Run

```bash
# Using the unified script (recommended)
./run_java_client.sh

# Using the JAR directly
java -jar java/target/vibrent-api-client-1.0.0.jar

# With custom config file
java -jar java/target/vibrent-api-client-1.0.0.jar path/to/config.yaml

# Using Maven
cd java && mvn exec:java -Dexec.mainClass="com.vibrenthealth.apiclient.RunExport"
```

## Configuration Reference

The config file (`shared/config/vibrent_config.yaml`) uses independent sections per export type. See `shared/config/sample_config.yaml` for all options with inline documentation.

### Environment Setup

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

auth:
  timeout: 30
  refresh_buffer: 300

api:
  timeout: 60
```

### Survey V1 Export (Config-Driven)

The Java client runs survey V1 exports via config. Each form gets its own export request.

```yaml
survey_export:
  use_date_range: true        # false = export ALL data (wide date range)

  date_range:
    default_days_back: 7      # relative: last N days
    # absolute_start_date: "2024-01-01"  # overrides default_days_back
    # absolute_end_date: "2024-12-31"

  split_date_range: false     # true = chunk large ranges (recommended for >6 months)
  format: "JSON"              # JSON or CSV

  request:
    max_surveys: null          # null = all surveys
    survey_ids: null           # [123, 456] = only these
    exclude_survey_ids: null   # [999] = skip these

  monitoring:
    polling_interval: 10
    max_wait_time: null
    continue_on_failure: true
```

### `use_date_range` Behavior

| Setting | Behavior |
|---------|----------|
| `true`  | Uses the `date_range` section (relative or absolute) |
| `false` | Sends wide date range (Jan 1, 2000 to now) to pull ALL data |

## Programmatic Usage

For export types beyond survey V1, use the Java SDK classes directly. All export types are available programmatically.

### Survey V1 (Deprecated)

```java
import com.vibrenthealth.apiclient.core.*;
import com.vibrenthealth.apiclient.models.*;

ConfigManager configManager = new ConfigManager("shared/config/vibrent_config.yaml");
VibrentHealthAPIClient client = new VibrentHealthAPIClient(configManager, "staging");

// List available surveys
List<Survey> surveys = client.getSurveys();
System.out.println("Found " + surveys.size() + " surveys");

// Export a specific survey — format is required ("JSON" or "CSV")
ExportRequest request = new ExportRequest();
request.setDateFrom(1746490800000L);
request.setDateTo(1747700400000L);
request.setFormat("JSON");
String exportId = client.requestSurveyExport(1700, request);
```

### Survey V2 (Wide Format) - Recommended to export the Survey Responses

```java
WideFormatReportRequest v2Request = new WideFormatReportRequest();
v2Request.setDateFrom(1746490800000L);
v2Request.setDateTo(1747700400000L);
v2Request.setFileType("CSV");           // CSV or JSON
v2Request.setRemovePII(true);           // exclude PII
v2Request.setCompletedOnly(true);       // only completed responses
v2Request.setUserType("REAL_ONLY");     // REAL_ONLY | TEST_ONLY | ALL_USERS
v2Request.setChoiceValueFormat("VALUE_AND_TEXT"); // VALUE_ONLY | TEXT_ONLY | VALUE_AND_TEXT
String exportId = client.requestSurveyV2Export(1700, v2Request);
```

### EHR Export

```java
// Single participant — no date range limit
EHRExportRequest ehrRequest = new EHRExportRequest();
ehrRequest.setDateFrom(1746490800000L);
ehrRequest.setDateTo(1747700400000L);
String exportId = client.requestEhrExport(24291L, ehrRequest);

// Multi data mode — max 100 participants, max 24h
EHRExportRequest multiData = new EHRExportRequest();
multiData.setDateFrom(1747614000000L);
multiData.setDateTo(1747700400000L);
multiData.setParticipantIds(List.of(24291L, 24365L));
multiData.setManifestOnly(false);
exportId = client.requestMultiEhrExport(multiData);

// Multi manifest mode — unlimited participants, max 360 days
EHRExportRequest manifest = new EHRExportRequest();
manifest.setDateFrom(1747100000000L);
manifest.setDateTo(1747700400000L);
manifest.setManifestOnly(true);
exportId = client.requestMultiEhrExport(manifest);
```

### Device Data Export

```java
// Single participant — max 24h
DeviceDataExportRequest deviceRequest = new DeviceDataExportRequest();
deviceRequest.setDateFrom(1747614000000L);
deviceRequest.setDateTo(1747700400000L);
deviceRequest.setManifestOnly(false);
String exportId = client.requestDeviceExport(23760L, deviceRequest);

// Multi with filters — max 100 participants, max 24h
// deviceTypes: FITBIT, GARMIN, APPLE_HEALTHKIT
// dataTypes:   SLEEP, STEPS, HEART_RATE, ACTIVITY, DISTANCE, RESPIRATORY, STRESS, DAILY_SUMMARY
DeviceDataExportRequest multiDevice = new DeviceDataExportRequest();
multiDevice.setDateFrom(1747614000000L);
multiDevice.setDateTo(1747700400000L);
multiDevice.setParticipantIds(List.of(23760L, 23757L));
multiDevice.setDeviceTypes(List.of("FITBIT"));
multiDevice.setDataTypes(List.of("SLEEP", "HEART_RATE"));
multiDevice.setManifestOnly(false);
exportId = client.requestMultiDeviceExport(multiDevice);

// Manifest mode — unlimited participants, max 360 days
DeviceDataExportRequest deviceManifest = new DeviceDataExportRequest();
deviceManifest.setDateFrom(1747100000000L);
deviceManifest.setDateTo(1747700400000L);
deviceManifest.setManifestOnly(true);
exportId = client.requestMultiDeviceExport(deviceManifest);
```

### Communication Events Export

```java
// Data mode — max 100 participants, max 24h
// IMPORTANT: participantIds must be Strings
// eventSources: ITERABLE, SES, TWILIO
// eventTypes:   EMAIL_SENT, EMAIL_DELIVERY, EMAIL_OPEN, EMAIL_CLICK,
//               EMAIL_BOUNCE, EMAIL_COMPLAINT, EMAIL_UNSUBSCRIBE, EMAIL_SEND_SKIP,
//               SMS_SEND, SMS_DELIVERED, SMS_BOUNCE, SMS_SEND_SKIP
CommunicationEventsExportRequest commsRequest = new CommunicationEventsExportRequest();
commsRequest.setDateFrom(1747614000000L);
commsRequest.setDateTo(1747700400000L);
commsRequest.setParticipantIds(List.of("9512", "9525"));
commsRequest.setManifestOnly(false);
String exportId = client.requestCommunicationEventsExport(commsRequest);

// Manifest mode — unlimited participants, max 360 days
CommunicationEventsExportRequest commsManifest = new CommunicationEventsExportRequest();
commsManifest.setDateFrom(1746490800000L);
commsManifest.setDateTo(1747700400000L);
commsManifest.setManifestOnly(true);
exportId = client.requestCommunicationEventsExport(commsManifest);
```

### Participant Profiles Export

```java
// Specific participants — participantIds must be Strings, max 1000
ParticipantProfilesExportRequest profilesRequest = new ParticipantProfilesExportRequest();
profilesRequest.setParticipantIds(List.of("9512", "9525"));
String exportId = client.requestParticipantProfilesExport(profilesRequest);

// All participants — omit participantIds
ParticipantProfilesExportRequest allProfiles = new ParticipantProfilesExportRequest();
exportId = client.requestParticipantProfilesExport(allProfiles);
```

### Bulk Survey Export

Export multiple (or all) surveys in a single API call.

```java
import com.vibrenthealth.apiclient.models.BulkSurveyExportRequest;

// All surveys — max 30 days date range
BulkSurveyExportRequest.SurveyData allData = new BulkSurveyExportRequest.SurveyData(true, null);
BulkSurveyExportRequest allRequest = new BulkSurveyExportRequest(
    System.currentTimeMillis() - (30L * 24 * 60 * 60 * 1000), // 30 days ago
    System.currentTimeMillis(),
    "JSON",
    false,  // removePII
    false,  // includeLabels
    allData
);
String exportId = client.requestBulkSurveyExport(allRequest);

// Specific surveys by ID — max 30 days if more than one survey
BulkSurveyExportRequest.SurveyData specificData =
    new BulkSurveyExportRequest.SurveyData(false, List.of(101, 202, 303));
BulkSurveyExportRequest specificRequest = new BulkSurveyExportRequest(
    System.currentTimeMillis() - (30L * 24 * 60 * 60 * 1000),
    System.currentTimeMillis(),
    "JSON",
    true,   // removePII
    true,   // includeLabels
    specificData
);
exportId = client.requestBulkSurveyExport(specificRequest);
```

### Check Status and Download

```java
// Poll status
ExportStatus status = client.getExportStatus(exportId);
System.out.println("Status: " + status.getStatus());
// Statuses: SUBMITTED, IN_PROGRESS, COMPLETED, FAILED, NO_DATA

// Download when COMPLETED
Path outputDir = Path.of("output");
Path file = client.downloadExport(exportId, outputDir);
System.out.println("Downloaded: " + file);
```

## API Restrictions Quick Reference

| Export Type | Mode | Max Participants | Max Date Range | PID Type |
|-------------|------|-----------------|----------------|----------|
| EHR single | `/ehr/{pid}/request` | 1 (URL) | No limit | Integer |
| EHR multi data | `manifestOnly=false` | 100 | 24 hours | Integer |
| EHR multi manifest | `manifestOnly=true` | Unlimited | 360 days | Integer |
| Device single | `/device/{pid}/request` | 1 (URL) | 24 hours | Integer |
| Device multi data | `manifestOnly=false` | 100 | 24 hours | Integer |
| Device multi manifest | `manifestOnly=true` | Unlimited | 360 days | Integer |
| Comms data | `manifestOnly=false` | 100 | 24 hours | **String** |
| Comms manifest | `manifestOnly=true` | Unlimited | 360 days | **String** |
| Profiles | N/A | 1,000 | Optional | **String** |
| Survey V1 | `/survey/{id}/request` | N/A | Required | N/A |
| Survey V2 | `/v2/survey/{id}/request` | N/A | Required | N/A |
| Bulk Survey | `allSurveys` or multi-ID | N/A | 30 days | N/A |

## Project Structure

```
java/
├── src/main/java/com/vibrenthealth/apiclient/
│   ├── core/
│   │   ├── AuthenticationManager.java
│   │   ├── ConfigManager.java
│   │   ├── Constants.java
│   │   ├── SurveyDataExporter.java
│   │   └── VibrentHealthAPIClient.java
│   ├── models/
│   │   ├── BulkSurveyExportRequest.java
│   │   ├── CommunicationEventsExportRequest.java
│   │   ├── DeviceDataExportRequest.java
│   │   ├── EHRExportRequest.java
│   │   ├── ExportMetadata.java
│   │   ├── ExportRequest.java
│   │   ├── ExportStatus.java
│   │   ├── ParticipantProfilesExportRequest.java
│   │   ├── Survey.java
│   │   └── WideFormatReportRequest.java
│   ├── utils/
│   │   └── Helpers.java
│   └── RunExport.java
├── pom.xml
└── README.md
```

## Building and Testing

```bash
# Build
mvn clean package

# Run tests
mvn test
```

## Logging

Uses SLF4J with Logback. Configure in `src/main/resources/logback.xml`.

- Console: INFO and above
- File: `java/output/logs/vibrent-api-client.log` with rolling policy

Enable debug: `<logger name="com.vibrenthealth.apiclient" level="DEBUG" />`

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Token expired or wrong credentials | Check `VIBRENT_CLIENT_ID` / `VIBRENT_CLIENT_SECRET` |
| 400 `format is required` | Survey V1 missing format | Set `format: "JSON"` in config or request |
| 400 date range >24h | Data mode limit exceeded | Use ≤23h range or `manifestOnly: true` |
| 400 participantIds required | Data mode needs participant IDs | Add participantIds or use manifest mode |
| FAILED status | Server-side job error | Check `failureReason` in status response |
| 400 invalid survey id | Survey doesn't exist in program | Check `/api/ext/forms` for valid IDs |
| Configuration not found | Missing config file | Copy `sample_config.yaml` to `vibrent_config.yaml` |

## Documentation

- See `shared/config/sample_config.yaml` for all configuration options with inline docs
- See the main repository `README.md` for cross-language details

## License

This is a reference implementation provided by Vibrent Health. Please refer to the main project license for terms and conditions.
