"""
Exporters package for Vibrent Health API Client

This package contains concrete implementations of exporters for different
data types (surveys, EHR, devices, etc.).
"""

from .survey_exporter import SurveyExporter
from .survey_v2_exporter import SurveyV2Exporter
from .ehr_exporter import EHRExporter
from .device_exporter import DeviceExporter
from .participant_profiles_exporter import ParticipantProfilesExporter
from .communication_events_exporter import CommunicationEventsExporter

# Register exporters with the factory
from ..core.exporter_factory import ExporterFactory

ExporterFactory.register_exporter('survey', SurveyExporter)
ExporterFactory.register_exporter('survey_v2', SurveyV2Exporter)
ExporterFactory.register_exporter('ehr', EHRExporter)
ExporterFactory.register_exporter('device', DeviceExporter)
ExporterFactory.register_exporter('participant_profiles', ParticipantProfilesExporter)
ExporterFactory.register_exporter('communication_events', CommunicationEventsExporter)

__all__ = [
    'SurveyExporter',
    'SurveyV2Exporter',
    'EHRExporter',
    'DeviceExporter',
    'ParticipantProfilesExporter',
    'CommunicationEventsExporter',
]
