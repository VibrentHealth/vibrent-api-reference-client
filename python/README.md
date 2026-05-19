# Vibrent Health API Client (Python)

This directory contains the Python reference implementation for accessing Vibrent Health APIs.

## Setup

### Option A: Using the unified script (recommended)
```bash
# From the parent directory
./run_python_client.sh
```

### Option B: Manual setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the client:
   - Edit `shared/config/vibrent_config.yaml` to set your API URLs, credentials, and export options.
   - The default output directory is now `python/output/`.

3. Run the export:
   ```bash
   python run_export_new.py
   ```

## Output
- All exported data will be saved in `python/output/` by default.
- Log files will be saved in `python/output/logs/` with timestamps.
- Survey data files are organized in `survey_responses/` subdirectories with clear naming:
  - Individual parts: `survey_name_part_1.json`, `survey_name_part_2.json`, etc.
  - Merged files: `survey_name_merged.json` (combines all parts)
- All timestamps use UTC timezone for consistency.

## Bulk Survey Export

Export multiple (or all) surveys in a single API call instead of one request per survey.

```python
from vibrent_api_client.models import BulkSurveyExportRequest

# Export all surveys for the program
request = BulkSurveyExportRequest(
    dateFrom=1716019200000,
    dateTo=1716105600000,
    format="JSON",
    allSurveys=True,
    removePII=False,
    includeLabels=False,
)
export_id = client.request_bulk_survey_export(request)

# Export specific surveys by ID
request = BulkSurveyExportRequest(
    dateFrom=1716019200000,
    dateTo=1716105600000,
    format="JSON",
    allSurveys=False,
    surveyIds=[101, 202, 303],
    removePII=True,
    includeLabels=True,
)
export_id = client.request_bulk_survey_export(request)
```

## Documentation
- See the main repository `README.md` and `CONFIGURATION.md` for cross-language details.
- See this file for Python-specific instructions. 