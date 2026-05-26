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

### Initial Setup (One Time Only)

**Step 1: Install**

```bash
cd vibrent-api-reference-client
./run_python_client.sh --setup
```

This installs all required software. You only need to do this once.

**Step 2: Set Your Credentials**

You will receive a **Client ID** and **Client Secret** from the Vibrent team. Set them in your terminal before running any export:

```bash
export VIBRENT_CLIENT_ID="your_client_id"
export VIBRENT_CLIENT_SECRET="your_client_secret"
```

> You must run these two lines every time you open a new terminal window.

**Step 3: Create Your Configuration File**

```bash
cp shared/config/sample_config.yaml shared/config/vibrent_config.yaml
```

Open `shared/config/vibrent_config.yaml` in any text editor. Set your environment URLs:

```yaml
environments:
  staging:
    base_url: "https://your-researchcloud-url.com"
    token_url: "https://your-keycloak-url.com/auth/realms/your_realm/protocol/openid-connect/token"
```

---

### Export Types

---

#### 1. Survey V1 (One Form at a Time) - Deprecated. Please use Survey V2

**What it does:** Exports survey response data. It fetches the list of available forms in your program, then exports each form one by one.

**Command:**

```bash
./run_python_client.sh --export-type survey
```

**Configuration section:** `survey_export`

**Settings:**

- `use_date_range` — Set to `true` to filter by date, or `false` to export ALL responses regardless of date.
- `default_days_back` — Number of days to look back. Example: `30` exports the last 30 days of responses.
- `format` — **Required.** Set to `"JSON"` or `"CSV"` for your output format.
- `survey_ids` — Set to a list like `[1700, 1701]` to export only those specific forms. Set to `null` to export all forms.
- `exclude_survey_ids` — Set to a list like `[999, 888]` to skip specific forms. Ignored if `survey_ids` is set.
- `max_surveys` — Set a number to limit how many forms to export. Set to `null` for no limit.

**Restrictions:** No date range limit. No participant limit.

**Example — Export one specific form for the last 7 days in JSON:**

```yaml
survey_export:
  use_date_range: true
  date_range:
    default_days_back: 7
  format: "JSON"
  request:
    survey_ids: [1700]
```

---

#### 2. Survey V2 (Wide Format)

**What it does:** Exports survey data in "wide format" — one row per participant with all questions as columns. Supports PII removal and filtering by user type.

**Command:**

```bash
./run_python_client.sh --export-type survey_v2
```

**Configuration section:** `survey_v2_export`

**Settings:**

- `use_date_range` — `true` or `false`. Set `false` to export ALL responses.
- `default_days_back` — Number of days to look back.
- `file_type` — `"CSV"` or `"JSON"`. CSV is recommended for wide format.
- `remove_pii` — Set to `true` to strip personally identifiable information from the export.
- `completed_only` — Set to `true` to export only completed responses.
- `user_type` — Choose who to include:
  - `"REAL_ONLY"` — Only real participants
  - `"TEST_ONLY"` — Only test accounts
  - `"ALL_USERS"` — Both real and test
- `choice_value_format` — How multiple choice answers appear:
  - `"VALUE_ONLY"` — Just the number (e.g., "1")
  - `"TEXT_ONLY"` — Just the text (e.g., "Strongly Agree")
  - `"VALUE_AND_TEXT"` — Both (e.g., "1 - Strongly Agree")
- `survey_ids` — Specific form IDs, or `null` for all.

**Restrictions:** No date range limit. No participant limit.

**Example — Export form 1700 as CSV without PII for real participants only:**

```yaml
survey_v2_export:
  use_date_range: true
  date_range:
    default_days_back: 30
  file_type: "CSV"
  remove_pii: true
  completed_only: true
  user_type: "REAL_ONLY"
  request:
    survey_ids: [1700]
```

---

#### 3. Bulk Survey (Multiple Forms in One Request) - Deprecated. Please use Survey V2

**What it does:** Exports multiple surveys (or all surveys) in a single request, instead of one at a time.

**Command:**

```bash
./run_python_client.sh --export-type bulk_survey
```

**Configuration section:** `bulk_survey_export`

**Settings:**

- `use_date_range` — Set to `true`. Date range is required for bulk exports.
- `default_days_back` — Number of days. **Maximum 30 days** when exporting all surveys or more than 1 survey.
- `format` — `"JSON"` or `"CSV"`.
- `all_surveys` — Set to `true` to export every form in the program. Set to `false` to use `survey_ids`.
- `survey_ids` — List of specific form IDs. Only used when `all_surveys` is `false`.
- `exclude_survey_ids` — List of form IDs to exclude. Works with both `all_surveys: true` and `false`.

**Restrictions:**

- When `all_surveys: true` or more than 1 survey — **maximum 30 days** date range.
- Single survey — no date range limit.

**Example — Export all surveys except form 999 for the last 20 days:**

```yaml
bulk_survey_export:
  use_date_range: true
  date_range:
    default_days_back: 20
  format: "JSON"
  request:
    all_surveys: true
    exclude_survey_ids: [999]
```

---

#### 4. EHR (Electronic Health Records)

**What it does:** Exports EHR/clinical data for specified participants.

**Command:**

```bash
./run_python_client.sh --export-type ehr
```

**Configuration section:** `ehr_export`

**Settings:**

- `use_date_range` — `true` or `false`.
- `default_days_back` — Number of days. See restrictions below.
- `participant_ids` — **Required.** List of participant IDs, e.g., `[24291, 24365]`.
- `manifest_only` — Set to `true` to export only metadata (no data files). Set to `false` to export full data.
- `exclude_participant_ids` — List of participant IDs to skip, or `null`.
- `max_participants` — Number to limit how many participants, or `null`.

**Restrictions:**

**Single participant (1 ID in the list):**
- `manifest_only: false` — **No date range limit.** You can export years of data.
- `manifest_only: true` — **No date range limit.** Single participant always uses the unrestricted endpoint.

**Multiple participants (2 or more IDs in the list):**
- `manifest_only: false` — Date range **maximum 24 hours**. Maximum **100 participants**.
- `manifest_only: true` — Date range **maximum 360 days**. **Unlimited participants**.

**Example A — One participant, full data, 4 years of history:**

```yaml
ehr_export:
  use_date_range: true
  date_range:
    default_days_back: 1460
  participant_ids: [24291]
  manifest_only: false
```

**Example B — Multiple participants, manifest only, 300 days:**

```yaml
ehr_export:
  use_date_range: true
  date_range:
    default_days_back: 300
  participant_ids: [24291, 24365, 23760]
  manifest_only: true
```

---

#### 5. Device Data (Wearables — Fitbit, Garmin, Apple HealthKit)

**What it does:** Exports wearable device data (sleep, steps, heart rate, activity, etc.) for specified participants.

**Command:**

```bash
./run_python_client.sh --export-type device
```

**Configuration section:** `device_export`

**Settings:**

- `use_date_range` — `true` or `false`.
- `default_days_back` — Number of days. See restrictions below.
- `participant_ids` — **Required.** List of participant IDs.
- `manifest_only` — `true` for metadata only, `false` for full data.
- `device_types` — Filter by device source. Set to `[]` for all devices. Options: `"FITBIT"`, `"GARMIN"`, `"APPLE_HEALTHKIT"`
- `data_types` — Filter by data type. Set to `[]` for all types. Options: `"SLEEP"`, `"STEPS"`, `"HEART_RATE"`, `"ACTIVITY"`, `"DISTANCE"`, `"RESPIRATORY"`, `"STRESS"`, `"DAILY_SUMMARY"`
- `exclude_participant_ids` — Participant IDs to skip, or `null`.

**Restrictions:**

Unlike EHR, there is **no special single-participant exception** for Device. The limits are the same regardless of how many participants you have:

- `manifest_only: false` — Date range **maximum 24 hours**. Maximum **100 participants**.
- `manifest_only: true` — Date range **maximum 360 days**. **Unlimited participants**.

**Example — Fitbit sleep data for 2 participants, last 23 hours:**

```yaml
device_export:
  use_date_range: true
  date_range:
    default_days_back: 1
  participant_ids: [23760, 23757]
  manifest_only: false
  device_types: ["FITBIT"]
  data_types: ["SLEEP"]
```

---

#### 6. Participant Profiles

**What it does:** Exports participant profile/user property data (demographics, enrollment info, etc.). This does NOT use date ranges — it always exports the current profile data.

**Command:**

```bash
./run_python_client.sh --export-type participant_profiles
```

**Configuration section:** `participant_profiles_export`

**Settings:**

- `participant_ids` — List of participant IDs, or empty list `[]` to export ALL participants.
- `max_participants` — Number to limit, or `null`. API hard limit is **1,000 per request**.
- `exclude_participant_ids` — Participant IDs to skip, or `null`.

**Restrictions:**

- **No date range** — always exports current profile data.
- **Maximum 1,000 participants** per request.
- Empty participant list `[]` exports ALL participants in the program.

**Example — Export profiles for all participants:**

```yaml
participant_profiles_export:
  use_date_range: false
  participant_ids: []
```

---

#### 7. Communication Events (Email & SMS)

**What it does:** Exports email and SMS communication event data — when emails were sent, delivered, opened, bounced, etc.

**Command:**

```bash
./run_python_client.sh --export-type communication_events
```

**Configuration section:** `communication_events_export`

**Settings:**

- `use_date_range` — `true` or `false`.
- `default_days_back` — Number of days. See restrictions below.
- `participant_ids` — List of participant IDs, or empty list `[]` for ALL participants.
- `manifest_only` — `true` for metadata only, `false` for full data.
- `event_sources` — Filter by platform. Set to `[]` for all sources. Options: `"ITERABLE"`, `"SES"`, `"TWILIO"`
- `event_types` — Filter by event type. Set to `[]` for all types. Options:
  - Email: `"EMAIL_SENT"`, `"EMAIL_DELIVERY"`, `"EMAIL_OPEN"`, `"EMAIL_CLICK"`, `"EMAIL_BOUNCE"`, `"EMAIL_COMPLAINT"`, `"EMAIL_UNSUBSCRIBE"`, `"EMAIL_SEND_SKIP"`
  - SMS: `"SMS_SEND"`, `"SMS_DELIVERED"`, `"SMS_BOUNCE"`, `"SMS_SEND_SKIP"`
- `exclude_participant_ids` — Participant IDs to skip, or `null`.

**Restrictions:**

- `manifest_only: false` — Date range **maximum 24 hours**. Maximum **100 participants**.
- `manifest_only: true` — Date range **maximum 360 days**. **Unlimited participants**.

**Example — All email events for 2 participants, last 23 hours:**

```yaml
communication_events_export:
  use_date_range: true
  date_range:
    default_days_back: 1
  participant_ids: [9512, 9525]
  manifest_only: false
  event_sources: []
  event_types: ["EMAIL_SENT", "EMAIL_DELIVERY", "EMAIL_OPEN"]
```

---

### Quick Reference — All Restrictions

**Survey Exports:**

- **Survey V1** — No date range limit. No participant limit. One form at a time.
- **Survey V2** — No date range limit. No participant limit. Wide format with PII removal.
- **Bulk Survey** — Maximum 30 days when exporting all surveys or more than 1 survey. Single survey has no limit.

**EHR Export:**

- **1 participant** — No date range limit regardless of manifest_only setting.
- **2+ participants, manifest_only: false** — Maximum 24 hours, maximum 100 participants.
- **2+ participants, manifest_only: true** — Maximum 360 days, unlimited participants.

**Device Data Export:**

- **manifest_only: false** — Maximum 24 hours, maximum 100 participants (same for 1 or many).
- **manifest_only: true** — Maximum 360 days, unlimited participants.

**Participant Profiles:**

- No date range. Maximum 1,000 participants per request. Empty list exports all.

**Communication Events:**

- **manifest_only: false** — Maximum 24 hours, maximum 100 participants.
- **manifest_only: true** — Maximum 360 days, unlimited participants.

---

### Where Do Exported Files Go?

All exported files are saved to the `output/` directory inside the `python/` folder, organized by export type:

```
output/
  survey_exports/
  ehr_exports/
  device_exports/
  participant_profiles_exports/
  communication_events_exports/
```

---

### Helpful Commands

```bash
# List all available export types
./run_python_client.sh --list-types

# Use a custom config file
./run_python_client.sh --export-type survey --config path/to/my_config.yaml
```

---

### Config-Driven Troubleshooting

**401 Unauthorized** — Wrong or expired credentials. Check your `VIBRENT_CLIENT_ID` and `VIBRENT_CLIENT_SECRET`.

**400 "Date range cannot exceed 24 hours"** — You are in data mode (`manifest_only: false`) with a date range larger than 24 hours. Either reduce `default_days_back` to 1, or set `manifest_only: true`.

**400 "Date range cannot exceed 360 days"** — You are in manifest mode (`manifest_only: true`) with a date range larger than 360 days. Reduce `default_days_back` to 360 or less.

**400 "format is required"** — Survey V1 export requires the `format` field. Set `format: "JSON"` or `format: "CSV"` in the `survey_export` config.

**400 "participantIds required"** — Data mode (`manifest_only: false`) requires participant IDs. Add participant IDs to your config, or switch to `manifest_only: true`.

**No data exported** — There is no data in the date range you specified. Try a wider date range.

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
