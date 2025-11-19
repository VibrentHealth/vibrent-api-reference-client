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

# Core components
from .core.auth import AuthenticationManager
from .core.client import VibrentHealthAPIClient
from .core.config import ConfigManager

# New architecture (v2.0+)
from .core.base_exporter import BaseExporter
from .core.orchestrator import ExportOrchestrator
from .core.exporter_factory import ExporterFactory

# Legacy components (deprecated but maintained for backward compatibility)
from .core.exporter import SurveyDataExporter

# Exporters
from .exporters import SurveyExporter, SurveyV2Exporter

# Models
from .models import Survey, ExportRequest, ExportStatus, ExportMetadata, WideFormatReportRequest

__version__ = "2.0.0"
__author__ = "Vibrent Health"

__all__ = [
    # Core
    "VibrentHealthAPIClient",
    "AuthenticationManager",
    "ConfigManager",
    # New architecture
    "BaseExporter",
    "ExportOrchestrator",
    "ExporterFactory",
    # Exporters
    "SurveyExporter",
    "SurveyV2Exporter",
    # Legacy (deprecated)
    "SurveyDataExporter",
    # Models
    "Survey",
    "ExportRequest",
    "ExportStatus",
    "ExportMetadata",
    "WideFormatReportRequest"
] 