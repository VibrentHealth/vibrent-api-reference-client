# Vibrent Health API Client (Python)

A config-driven client for exporting data from Vibrent Health APIs. Configure `vibrent_config.yaml`, set credentials, and run — the client handles authentication, form listing, export submission, polling, and download automatically.

## Prerequisites

- Python 3.7 or higher
- pip3
- Access to Vibrent Health APIs (client ID and secret)

## Quick Start

### 1. Setup

```bash
# From the repository root
./run_python_client.sh --setup

# Set credentials
export VIBRENT_CLIENT_ID="your_client_id"
export VIBRENT_CLIENT_SECRET="your_client_secret"
```

### 2. Configure

```bash
cp shared/config/sample_config.yaml shared/config/vibrent_config.yaml
# Edit vibrent_config.yaml — set your API URLs and export options
```

### 3. Run

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

## Configuration Reference

The config file (`shared/config/vibrent_config.yaml`) has independent sections per export type. See `shared/config/sample_config.yaml` for all options with inline documentation.

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

### Survey V1 Export (`--export-type survey`)

Exports survey response data per form. Each form gets its own export request.

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

### Bulk Survey Export (`--export-type bulk_survey`)

Exports multiple (or all) surveys in a single API call using `POST /api/ext/export/survey/request`.

```yaml
bulk_survey_export:
  use_date_range: true

  date_range:
    default_days_back: 30     # max 30 days for bulk exports

  format: "JSON"              # JSON or CSV
  remove_pii: false           # true = exclude PII
  include_labels: false       # true = include question labels

  request:
    all_surveys: true          # true = all surveys in one request
    survey_ids: null           # [123, 456] = only these (when all_surveys is false)
    exclude_survey_ids: null   # [999] = skip these (when all_surveys is false)

  monitoring:
    polling_interval: 10
    max_wait_time: null
    continue_on_failure: true
```

**API restrictions:** max 30 days date range when `all_surveys: true` or more than one survey ID.

### Survey V2 Export (`--export-type survey_v2`)

Wide-format export with PII removal, user type filtering, and choice value formatting.

```yaml
survey_v2_export:
  use_date_range: true

  date_range:
    default_days_back: 30

  split_date_range: false
  file_type: "CSV"              # CSV or JSON
  remove_pii: false             # true = exclude PII
  completed_only: true          # true = only completed responses
  include_withdrawn_user: true
  combine_values_for_multiple_choices: true

  # VALUE_ONLY | TEXT_ONLY | VALUE_AND_TEXT
  choice_value_format: "VALUE_AND_TEXT"

  # REAL_ONLY | TEST_ONLY | ALL_USERS
  user_type: "REAL_ONLY"

  request:
    max_surveys: null
    survey_ids: null
    exclude_survey_ids: null
```

### EHR Export (`--export-type ehr`)

Exports Electronic Health Records per participant (FHIR R4 format).

```yaml
ehr_export:
  use_date_range: true

  date_range:
    default_days_back: 1460   # ~4 years

  split_date_range: false

  # Required: list of integer participant IDs
  participant_ids: [24291, 24365]
  max_participants: null
  exclude_participant_ids: null
```

**API restrictions:**
- Single participant (`/ehr/{pid}/request`): no date range limit
- Multi data mode (`manifestOnly: false`): max 100 participants, max 24 hours
- Multi manifest mode (`manifestOnly: true`): unlimited participants, max 360 days

### Device Data Export (`--export-type device`)

Exports wearable/device data with optional device and data type filters.

```yaml
device_export:
  use_date_range: true

  date_range:
    default_days_back: 90

  split_date_range: false

  participant_ids: [23760, 23757]
  max_participants: null
  exclude_participant_ids: null

  # Filter by device source (empty = all)
  # Options: FITBIT, GARMIN, APPLE_HEALTHKIT
  device_types: []

  # Filter by data type (empty = all)
  # Options: SLEEP, STEPS, HEART_RATE, ACTIVITY, DISTANCE, RESPIRATORY, STRESS, DAILY_SUMMARY
  data_types: []

  manifest_only: false        # true = metadata only (no data files)
```

**API restrictions:**
- Single participant: max 24 hours
- Multi data mode (`manifestOnly: false`): max 100 participants, max 24 hours
- Multi manifest mode (`manifestOnly: true`): unlimited participants, max 360 days

### Participant Profiles Export (`--export-type participant_profiles`)

Exports current participant profile/user property data. No date range required.

```yaml
participant_profiles_export:
  use_date_range: false       # profiles don't use date ranges

  # Integer IDs in config, auto-converted to strings for API
  # Empty [] or null = export ALL participants
  participant_ids: []
  max_participants: null
  exclude_participant_ids: null
```

**API restrictions:** max 1,000 participants per request. `participantIds` are strings in the API.

### Communication Events Export (`--export-type communication_events`)

Exports email and SMS communication event data.

```yaml
communication_events_export:
  use_date_range: true

  date_range:
    default_days_back: 30

  split_date_range: false

  # Integer IDs in config, auto-converted to strings for API
  # Empty [] or null = ALL participants
  participant_ids: []
  max_participants: null
  exclude_participant_ids: null

  # Filter by source (empty = all)
  # Options: ITERABLE, SES, TWILIO
  event_sources: []

  # Filter by event type (empty = all)
  # Email: EMAIL_SENT, EMAIL_DELIVERY, EMAIL_OPEN, EMAIL_CLICK, EMAIL_BOUNCE,
  #        EMAIL_COMPLAINT, EMAIL_UNSUBSCRIBE, EMAIL_SEND_SKIP
  # SMS:   SMS_SEND, SMS_DELIVERED, SMS_BOUNCE, SMS_SEND_SKIP
  event_types: []

  manifest_only: false
```

**API restrictions:**
- Data mode (`manifestOnly: false`): max 100 participants, max 24 hours. `participantIds` required (strings).
- Manifest mode (`manifestOnly: true`): unlimited participants, max 360 days

## What It Does

The orchestrator (`run_export_new.py`) automates the full workflow:

1. Authenticates using client credentials (OAuth2)
2. Lists available forms (`GET /api/ext/forms`)
3. Applies config filters (survey_ids, exclude_survey_ids, max_surveys)
4. For each item: submits export request, polls status, downloads when complete
5. Saves files to `output/` directory with metadata

### `use_date_range` Behavior

| Setting | Behavior |
|---------|----------|
| `true`  | Uses the `date_range` section (relative or absolute) |
| `false` | Sends wide date range (Jan 1, 2000 to now) to pull ALL data |

## Output

```
python/output/
  survey_exports/           # or ehr_exports/, device_exports/, etc.
    survey_name_part_1.json
    survey_name_merged.json
  logs/
    export_2026-05-18_14-30-00.log
  export_metadata.json
```

## Export Status Lifecycle

```
SUBMITTED → IN_PROGRESS → COMPLETED → (download available)
                        → FAILED     → (check failureReason)
                        → NO_DATA    → (no data in date range)
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 401 Unauthorized | Token expired or wrong credentia<br/>ls | Check `VIBRENT_CLIENT_ID` / `VIBRENT_CLIENT_SECRET` |
| 400 `format is required` | Survey V1 missing format | Set `format: "JSON"` in config |
| 400 date range >24h | Data mode limit exceeded | Use ≤23h range or set `manifest_only: true` |
| 400 participantIds required | Data mode needs participant IDs | Add `participant_ids` in config or use manifest mode |
| FAILED status | Server-side job error | Check `failureReason` in status response |
| 400 invalid survey id | Survey doesn't exist in program | Run `--list-types` or check `/api/ext/forms` |
| Configuration not found | Missing config file | Copy `sample_config.yaml` to `vibrent_config.yaml` |

## Documentation

- See `shared/config/sample_config.yaml` for all configuration options with inline docs
- See the main repository `README.md` for cross-language details
