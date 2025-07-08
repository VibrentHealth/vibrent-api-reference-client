"""
Vibrent Health API Client - Reference Implementation

This is a reference implementation for accessing Vibrent Health APIs.
This code is provided as-is for reference purposes only.

IMPORTANT DISCLAIMERS:
- This is a reference implementation only, not intended for production use without testing
- Vibrent Health does not provide active support, updates, or technical assistance
- No version compatibility guarantees are provided
- Report issues to info@vibrenthealth.com
- Users are responsible for their own implementation and deployment
"""

from .core.auth import AuthenticationManager
from .core.client import VibrentHealthAPIClient
from .core.exporter import SurveyDataExporter
from .models import Survey, ExportRequest, ExportStatus, ExportMetadata

__version__ = "1.0.0"
__author__ = "Vibrent Health"

__all__ = [
    "VibrentHealthAPIClient",
    "SurveyDataExporter", 
    "AuthenticationManager",
    "Survey",
    "ExportRequest",
    "ExportStatus",
    "ExportMetadata"
] 