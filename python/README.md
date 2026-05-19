# Vibrent Health API Client (Python)

A Python client for exporting data from Vibrent Health APIs. Supports all export types: Survey V1, Survey V2, Bulk Survey, EHR, Device Data, Participant Profiles, and Communication Events.

## Prerequisites

- Python 3.7 or higher
- pip3
- Access to Vibrent Health APIs (client ID and secret)

## Setup

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API Restrictions Quick Reference

| Export Type | Mode | Max Participants | Max Date Range | PID Type |
|-------------|------|------------------|----------------|----------|
| EHR single | `/ehr/{pid}/request` | 1 (URL) | No limit | Integer |
| EHR multi data | `/ehr/request` `manifestOnly=false` | 100 | 24 hours | Integer |
| EHR multi manifest | `/ehr/request` `manifestOnly=true` | Unlimited | 360 days | Integer |
| Device single | `/device/{pid}/request` | 1 (URL) | 24 hours | Integer |
| Device multi data | `/device/request` `manifestOnly=false` | 100 | 24 hours | Integer |
| Device multi manifest | `/device/request` `manifestOnly=true` | Unlimited | 360 days | Integer |
| Comms data | `/communicationEvents/request` `manifestOnly=false` | 100 | 24 hours | **String** |
| Comms manifest | `/communicationEvents/request` `manifestOnly=true` | Unlimited | 360 days | **String** |
| Profiles | `/participantProfiles/request` | 1,000 | Optional | **String** |
| Survey V1 | `/survey/{id}/request` | N/A | Required | N/A |
| Survey V2 | `/v2/survey/{id}/request` | N/A | Required | N/A |
| Bulk Survey | `/survey/request` | N/A | Max 30 days (all/multi) | N/A |

---

## Recommended: Programmatic Usage (Python SDK)

The programmatic approach gives full control over request parameters and is the recommended way to use the client.

### Authenticate

```python
import os, sys, tempfile, yaml, time
sys.path.insert(0, "python/src")  # if running from repo root

from vibrent_api_client.core.config import ConfigManager
from vibrent_api_client.core.client import VibrentHealthAPIClient

os.environ["VIBRENT_CLIENT_ID"] = "<client-id>"
os.environ["VIBRENT_CLIENT_SECRET"] = "<your-secret>"

config = {
    "environment": {
        "default": "staging",
        "environments": {
            "staging": {
                "base_url": "<base-url>",
                "token_url": "<token-url>",
            }
        },
    },
    "auth": {"timeout": 30, "refresh_buffer": 300},
    "api": {"timeout": 60, "debug_logging": False},
    "output": {"base_directory": "output", "survey_exports_dir": "survey_exports",
               "extract_files": True, "remove_zip_after_extract": True},
    "metadata": {"save_metadata": False},
}

fd, config_path = tempfile.mkstemp(suffix=".yaml")
with os.fdopen(fd, "w") as f:
    yaml.dump(config, f)

config_manager = ConfigManager(config_path)
client = VibrentHealthAPIClient(config_manager, "staging")
client.auth_manager.authenticate()
print(f"Authenticated: {client.auth_manager.access_token[:20]}...")

os.unlink(config_path)
```

### Common Time Helpers

```python
now_ms  = int(time.time() * 1000)
h23_ago = int((time.time() - 82800) * 1000)    # 23 hours ago
d7_ago  = int((time.time() - 86400 * 7) * 1000)  # 7 days ago
d30_ago = int((time.time() - 86400 * 30) * 1000) # 30 days ago
```

### EHR Exports

```python
from vibrent_api_client.models import EHRExportRequest, EHRMultiExportRequest

# Single participant (no date range limit)
request = EHRExportRequest(dateFrom=d30_ago, dateTo=now_ms)
export_id = client.request_ehr_export(24291, request)

# Multi data mode (max 100 pids, max 24h)
request = EHRMultiExportRequest(
    dateFrom=h23_ago, dateTo=now_ms,
    participantIds=[24291, 24365],
    manifestOnly=False,
)
export_id = client.request_multi_ehr_export(request)

# Multi manifest mode (unlimited pids, max 360 days)
request = EHRMultiExportRequest(
    dateFrom=d7_ago, dateTo=now_ms,
    participantIds=None,
    manifestOnly=True,
)
export_id = client.request_multi_ehr_export(request)
```

### Device Data Exports

```python
from vibrent_api_client.models import DeviceDataExportRequest

# Single participant (max 24h)
request = DeviceDataExportRequest(dateFrom=h23_ago, dateTo=now_ms, manifestOnly=False)
export_id = client.request_device_export(23760, request)

# Multi with filters (max 100 pids, max 24h)
request = DeviceDataExportRequest(
    dateFrom=h23_ago, dateTo=now_ms,
    participantIds=[23760, 23757],
    deviceTypes=["FITBIT"],
    dataTypes=["SLEEP", "HEART_RATE"],
    manifestOnly=False,
)
export_id = client.request_multi_device_export(request)

# Manifest mode (unlimited pids, max 360 days)
request = DeviceDataExportRequest(
    dateFrom=d7_ago, dateTo=now_ms,
    manifestOnly=True,
)
export_id = client.request_multi_device_export(request)
```

### Communication Events Exports

```python
from vibrent_api_client.models import CommunicationEventsExportRequest

# Data mode — participantIds must be STRINGS (max 100 pids, max 24h)
request = CommunicationEventsExportRequest(
    dateFrom=h23_ago, dateTo=now_ms,
    participantIds=["9512", "9525"],
    manifestOnly=False,
)
export_id = client.request_communication_events_export(request)

# Manifest mode (unlimited pids, max 360 days)
request = CommunicationEventsExportRequest(
    dateFrom=d30_ago, dateTo=now_ms,
    manifestOnly=True,
)
export_id = client.request_communication_events_export(request)
```

### Participant Profiles Export

```python
from vibrent_api_client.models import ParticipantProfilesExportRequest

# Specific participants — participantIds must be STRINGS (max 1,000)
request = ParticipantProfilesExportRequest(participantIds=["9512", "9525"])
export_id = client.request_participant_profiles_export(request)

# All participants
request = ParticipantProfilesExportRequest(participantIds=None)
export_id = client.request_participant_profiles_export(request)
```

### Survey V1 Export

```python
from vibrent_api_client.models import ExportRequest

# format is REQUIRED ("JSON" or "CSV"), no date range limit
request = ExportRequest(dateFrom=d30_ago, dateTo=now_ms, format="JSON")
export_id = client.request_survey_export(1700, request)
```

### Survey V2 (Wide Format) Export

```python
from vibrent_api_client.models import WideFormatReportRequest

request = WideFormatReportRequest(
    dateFrom=d30_ago, dateTo=now_ms,
    fileType="CSV",
    removePII=True,
    completedOnly=True,
    userType="REAL_ONLY",
    choiceValueFormat="VALUE_AND_TEXT",
)
export_id = client.request_survey_v2_export(1700, request)
```

### Bulk Survey Export

```python
from vibrent_api_client.models import BulkSurveyExportRequest

# All surveys (max 30 days)
request = BulkSurveyExportRequest(
    dateFrom=d30_ago, dateTo=now_ms,
    format="JSON",
    removePII=False,
    includeLabels=False,
    allSurveys=True,
    surveyIds=[],
)
export_id = client.request_bulk_survey_export(request)

# Specific surveys (max 30 days when >1 survey)
request = BulkSurveyExportRequest(
    dateFrom=d30_ago, dateTo=now_ms,
    format="JSON",
    allSurveys=False,
    surveyIds=[1700, 1701],
)
export_id = client.request_bulk_survey_export(request)
```

### Check Status, List Surveys, Download

```python
from pathlib import Path

# Check status
status = client.get_export_status(export_id)
print(f"Status: {status.status}")              # SUBMITTED, IN_PROGRESS, COMPLETED, FAILED, NO_DATA
print(f"File: {status.fileName}")
print(f"Download: {status.downloadEndpoint}")  # only if COMPLETED

# List surveys
surveys = client.get_surveys()
print(f"Found {len(surveys)} surveys")
for s in surveys[:5]:
    print(f"  {s.formId}: {s.formName}")

# Download (when COMPLETED)
output_path = Path("output")
output_path.mkdir(exist_ok=True)
file_path = client.download_export(export_id, output_path)
print(f"Downloaded: {file_path}")
```

---

## Legacy: Config-Driven Export (Deprecated)

> **Note:** The config-driven utility will be discontinued in a future release. Please migrate to the programmatic SDK usage above.

Configure `vibrent_config.yaml`, set credentials, and run — the orchestrator handles authentication, form listing, export submission, polling, and download automatically.

### Setup

```bash
# From the repository root
./run_python_client.sh --setup

# Set credentials
export VIBRENT_CLIENT_ID="your_client_id"
export VIBRENT_CLIENT_SECRET="your_client_secret"
```

### Configure

```bash
cp shared/config/sample_config.yaml shared/config/vibrent_config.yaml
# Edit vibrent_config.yaml — set your API URLs and export options
```

### Run

```bash
# Survey V1 — per form, no date range limit, format required (JSON/CSV)
./run_python_client.sh --export-type survey

# Survey V2 — wide format, no date range limit, supports PII removal and user type filtering
./run_python_client.sh --export-type survey_v2

# Bulk Survey — all/multiple surveys in one request, max 30 days when all_surveys or >1 survey
./run_python_client.sh --export-type bulk_survey

# EHR — single: no limit | multi data: max 100 participants, max 24h | multi manifest: max 360 days
./run_python_client.sh --export-type ehr

# Device — single: max 24h | multi data: max 100 participants, max 24h | multi manifest: max 360 days
./run_python_client.sh --export-type device

# Participant Profiles — no date range required, max 1,000 participants per request
./run_python_client.sh --export-type participant_profiles

# Communication Events — data: max 100 participants, max 24h | manifest: max 360 days
./run_python_client.sh --export-type communication_events

# List all available export types
./run_python_client.sh --list-types

# Custom config file
./run_python_client.sh --export-type survey --config path/to/config.yaml
```

Or run directly with Python:

```bash
cd python
source venv/bin/activate
python run_export_new.py --export-type survey
python run_export_new.py --export-type ehr
```

### Configuration Reference

The config file (`shared/config/vibrent_config.yaml`) has independent sections per export type. See `shared/config/sample_config.yaml` for all options with inline documentation.

---

## Export Status Lifecycle

```
SUBMITTED -> IN_PROGRESS -> COMPLETED -> (download available)
                         -> FAILED     -> (check failureReason)
                         -> NO_DATA    -> (no data in date range)
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Token expired or wrong credentials | Check `VIBRENT_CLIENT_ID` / `VIBRENT_CLIENT_SECRET` |
| 400 `format is required` | Survey V1 missing format | Set `format: "JSON"` |
| 400 date range >24h | Data mode limit exceeded | Use <=23h range or set `manifestOnly: true` |
| 400 participantIds required | Data mode needs participant IDs | Add participantIds or use manifest mode |
| FAILED status | Server-side job error | Check `failureReason` in status response |
| 400 invalid survey id | Survey doesn't exist in program | Call `/api/ext/forms` to list valid IDs |

## Documentation

- See `shared/config/sample_config.yaml` for all configuration options with inline docs
- See the main repository `README.md` for cross-language details
- See [Export API Manual Test Guide](https://vibrenthealth.atlassian.net/wiki/spaces/DA/pages/15808954397) for curl examples and full API reference
