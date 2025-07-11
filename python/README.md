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
   python run_export.py
   ```

## Output
- All exported data will be saved in `python/output/` by default.
- Log files will be saved in `python/output/logs/` with timestamps.

## Documentation
- See the main repository `README.md` and `CONFIGURATION.md` for cross-language details.
- See this file for Python-specific instructions. 