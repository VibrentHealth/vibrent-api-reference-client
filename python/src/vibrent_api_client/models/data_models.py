#!/usr/bin/env python3
"""
Data models for Vibrent Health API Client

This module contains all the dataclasses used for API data structures.
"""

import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any


@dataclass
class Survey:
    """Represents a survey object from the API"""
    id: int
    name: str
    displayName: str
    platformFormId: int
    export_details: Optional[List[Dict]] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create Survey object from dictionary using JSON serialization"""
        # Define default values for required fields
        defaults = {
            'id': 0,
            'name': 'Unknown Survey',
            'displayName': 'Unknown Survey',
            'platformFormId': 0,
            'export_details': None
        }
        
        # Merge defaults with provided data
        merged_data = {**defaults, **data}
        
        # Use JSON serialization to handle field mapping
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExportRequest:
    """Represents an export request"""
    dateFrom: int
    dateTo: int
    format: str = "JSON"

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExportRequest object from dictionary using JSON serialization"""
        defaults = {
            'dateFrom': 0,
            'dateTo': 0,
            'format': 'JSON'
        }
        
        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExportStatus:
    """Represents the status of an export request"""
    exportId: str
    status: str
    fileName: Optional[str] = None
    submittedOn: Optional[str] = None
    completedOn: Optional[str] = None
    downloadEndpoint: Optional[str] = None
    failureReason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExportStatus object from dictionary using JSON serialization"""
        defaults = {
            'exportId': '',
            'status': 'UNKNOWN',
            'fileName': None,
            'submittedOn': None,
            'completedOn': None,
            'downloadEndpoint': None,
            'failureReason': None
        }
        
        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class WideFormatReportRequest:
    """
    Survey V2 export request with wide format and advanced options.

    This request type supports the V2 API endpoint with additional features like
    PII removal, wide format reporting, and data dictionary inclusion.
    """
    dateFrom: int
    dateTo: int
    fileType: str = "CSV"  # CSV or JSON
    removePII: bool = False
    completedOnly: bool = True
    includeWithdrawnUser: bool = True
    combineValuesForMultipleChoices: bool = True
    choiceValueFormat: str = "VALUE_AND_TEXT"  # VALUE_ONLY, TEXT_ONLY, VALUE_AND_TEXT
    userType: str = "REAL_ONLY"  # REAL_ONLY, TEST_ONLY, ALL_USERS

    @classmethod
    def from_dict(cls, data: dict):
        """Create WideFormatReportRequest object from dictionary"""
        defaults = {
            'dateFrom': 0,
            'dateTo': 0,
            'fileType': 'CSV',
            'removePII': False,
            'completedOnly': True,
            'includeWithdrawnUser': True,
            'combineValuesForMultipleChoices': True,
            'choiceValueFormat': 'VALUE_AND_TEXT',
            'userType': 'REAL_ONLY'
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class EHRExportRequest:
    """
    EHR data export request.

    Used for requesting Electronic Health Record (EHR) data exports for a participant.
    """
    dateFrom: Optional[int] = None
    dateTo:  Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create EHRExportRequest object from dictionary"""
        defaults = {
            'dateFrom': 0,
            'dateTo': 0
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Participant:
    """
    Represents a participant for EHR exports.

    Attributes:
        id: Participant's unique identifier
        external_id: Optional external identifier for the participant
        name: Optional participant name (for display purposes only)
    """
    id: int
    external_id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create Participant object from dictionary"""
        defaults = {
            'id': 0,
            'external_id': None,
            'name': None
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CommunicationEventsExportRequest:
    """
    Communication events export request.

    Used for requesting export of communication events data (email, SMS) for participants
    within a specified date range, with optional filtering by event source and type.

    This is a batch export - one request can export events for multiple participants.

    Special behavior:
    - participantIds null/empty: export for all participants in the program
    - dateFrom/dateTo optional: defaults to dateFrom=0, dateTo=current time if omitted
    - eventSources empty/null: export from all sources (ITERABLE, SES, TWILIO)
    - eventTypes empty/null: export all event types
    - participantIds must be strings (not integers), per API contract
    """
    participantIds: Optional[List[str]] = None
    dateFrom: Optional[int] = None
    dateTo: Optional[int] = None
    manifestOnly: bool = False
    eventSources: Optional[List[str]] = None
    eventTypes: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create CommunicationEventsExportRequest object from dictionary"""
        defaults = {
            'participantIds': None,
            'dateFrom': None,
            'dateTo': None,
            'manifestOnly': False,
            'eventSources': None,
            'eventTypes': None
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {}
        if self.participantIds is not None:
            result['participantIds'] = self.participantIds
        if self.dateFrom is not None:
            result['dateFrom'] = self.dateFrom
        if self.dateTo is not None:
            result['dateTo'] = self.dateTo
        result['manifestOnly'] = self.manifestOnly
        if self.eventSources is not None:
            result['eventSources'] = self.eventSources
        if self.eventTypes is not None:
            result['eventTypes'] = self.eventTypes
        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class CommunicationEventSource:
    """
    Communication platform sources for event filtering.

    These represent the communication platforms that generate events.
    """
    ITERABLE = "ITERABLE"
    SES = "SES"
    TWILIO = "TWILIO"

    @classmethod
    def get_all_sources(cls) -> List[str]:
        """Get list of all event sources"""
        return [cls.ITERABLE, cls.SES, cls.TWILIO]

    @classmethod
    def is_valid(cls, source: str) -> bool:
        """Check if event source is valid"""
        return source in cls.get_all_sources()


class CommunicationEventType:
    """
    Communication event types for filtering.

    These represent specific types of communication events across email, SMS, and other channels.
    """
    # Email events
    EMAIL_SENT = "EMAIL_SENT"
    EMAIL_DELIVERY = "EMAIL_DELIVERY"
    EMAIL_OPEN = "EMAIL_OPEN"
    EMAIL_CLICK = "EMAIL_CLICK"
    EMAIL_BOUNCE = "EMAIL_BOUNCE"
    EMAIL_COMPLAINT = "EMAIL_COMPLAINT"
    EMAIL_UNSUBSCRIBE = "EMAIL_UNSUBSCRIBE"
    EMAIL_SEND_SKIP = "EMAIL_SEND_SKIP"

    # SMS events
    SMS_SEND = "SMS_SEND"
    SMS_DELIVERED = "SMS_DELIVERED"
    SMS_BOUNCE = "SMS_BOUNCE"
    SMS_SEND_SKIP = "SMS_SEND_SKIP"

    # Other
    EVENT_TYPE = "EVENT_TYPE"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get list of all event types"""
        return [
            # Email
            cls.EMAIL_SENT,
            cls.EMAIL_DELIVERY,
            cls.EMAIL_OPEN,
            cls.EMAIL_CLICK,
            cls.EMAIL_BOUNCE,
            cls.EMAIL_COMPLAINT,
            cls.EMAIL_UNSUBSCRIBE,
            cls.EMAIL_SEND_SKIP,
            # SMS
            cls.SMS_SEND,
            cls.SMS_DELIVERED,
            cls.SMS_BOUNCE,
            cls.SMS_SEND_SKIP,
            # Other
            cls.EVENT_TYPE
        ]

    @classmethod
    def get_email_types(cls) -> List[str]:
        """Get list of email event types"""
        return [
            cls.EMAIL_SENT,
            cls.EMAIL_DELIVERY,
            cls.EMAIL_OPEN,
            cls.EMAIL_CLICK,
            cls.EMAIL_BOUNCE,
            cls.EMAIL_COMPLAINT,
            cls.EMAIL_UNSUBSCRIBE,
            cls.EMAIL_SEND_SKIP
        ]

    @classmethod
    def get_sms_types(cls) -> List[str]:
        """Get list of SMS event types"""
        return [
            cls.SMS_SEND,
            cls.SMS_DELIVERED,
            cls.SMS_BOUNCE,
            cls.SMS_SEND_SKIP
        ]

    @classmethod
    def is_valid(cls, event_type: str) -> bool:
        """Check if event type is valid"""
        return event_type in cls.get_all_types()


@dataclass
class ParticipantProfilesExportRequest:
    """
    Participant profiles (user properties) export request.

    Used for requesting export of participant profile/user property data.
    This is a batch export - one request can export multiple participants.

    Special behavior:
    - null or empty array: export ALL participants in the authenticated program
    - non-empty array: export only specified participants (max 1000 entries)
    - participantIds must be strings (not integers), per API contract
    """
    participantIds: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create ParticipantProfilesExportRequest object from dictionary"""
        defaults = {
            'participantIds': None
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values for 'export all' behavior"""
        result = {}
        if self.participantIds is not None:
            result['participantIds'] = self.participantIds
        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class DeviceDataExportRequest:
    """
    Device data export request.

    Used for requesting device data exports for a participant with optional filtering
    by device type, data type, and date range.
    """
    dateFrom: Optional[int] = None
    dateTo: Optional[int] = None
    deviceTypes: Optional[List[str]] = None
    dataTypes: Optional[List[str]] = None
    manifestOnly: bool = False

    @classmethod
    def from_dict(cls, data: dict):
        """Create DeviceDataExportRequest object from dictionary"""
        defaults = {
            'dateFrom': None,
            'dateTo': None,
            'deviceTypes': None,
            'dataTypes': None,
            'manifestOnly': False
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {}
        if self.dateFrom is not None:
            result['dateFrom'] = self.dateFrom
        if self.dateTo is not None:
            result['dateTo'] = self.dateTo
        if self.deviceTypes is not None:
            result['deviceTypes'] = self.deviceTypes
        if self.dataTypes is not None:
            result['dataTypes'] = self.dataTypes
        result['manifestOnly'] = self.manifestOnly
        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class DeviceType:
    """
    Device data source types (source_mapping).

    These map to internal device sources for device data exports.
    """
    FITBIT = "FITBIT"
    GARMIN = "GARMIN"
    APPLE_HEALTHKIT = "APPLE_HEALTHKIT"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get list of all device types"""
        return [cls.FITBIT, cls.GARMIN, cls.APPLE_HEALTHKIT]

    @classmethod
    def is_valid(cls, device_type: str) -> bool:
        """Check if device type is valid"""
        return device_type in cls.get_all_types()


class DeviceDataType:
    """
    Logical grouping of device data types (datatype_mapping).

    Each data type maps to source-specific payload types.
    """
    SLEEP = "SLEEP"
    STEPS = "STEPS"
    HEART_RATE = "HEART_RATE"
    ACTIVITY = "ACTIVITY"
    DISTANCE = "DISTANCE"
    RESPIRATORY = "RESPIRATORY"
    STRESS = "STRESS"
    DAILY_SUMMARY = "DAILY_SUMMARY"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get list of all data types"""
        return [
            cls.SLEEP,
            cls.STEPS,
            cls.HEART_RATE,
            cls.ACTIVITY,
            cls.DISTANCE,
            cls.RESPIRATORY,
            cls.STRESS,
            cls.DAILY_SUMMARY
        ]

    @classmethod
    def is_valid(cls, data_type: str) -> bool:
        """Check if data type is valid"""
        return data_type in cls.get_all_types()


@dataclass
class ExportMetadata:
    """Metadata for the export session"""
    export_session_id: str
    start_timestamp: str
    total_surveys: int
    successful_exports: int
    failed_exports: int
    output_directory: str
    surveys: List[Dict] = field(default_factory=list)
    failures: List[Dict] = field(default_factory=list)
    end_timestamp: Optional[str] = None
    duration_seconds: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict):
        """Create ExportMetadata object from dictionary using JSON serialization"""
        defaults = {
            'export_session_id': '',
            'start_timestamp': '',
            'total_surveys': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'output_directory': '',
            'surveys': [],
            'failures': [],
            'end_timestamp': None,
            'duration_seconds': None
        }

        merged_data = {**defaults, **data}
        json_str = json.dumps(merged_data)
        return cls(**json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
