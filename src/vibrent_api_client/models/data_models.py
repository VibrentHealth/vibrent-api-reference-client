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
    export_details: Optional[Dict] = None

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
