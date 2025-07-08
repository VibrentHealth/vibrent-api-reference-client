"""
Helper utilities for Vibrent Health API Client
"""

import logging
from datetime import datetime


def safe_from_dict(cls, data: dict, logger=None):
    """Safely create an object from dictionary using from_dict method if available"""
    try:
        if hasattr(cls, 'from_dict'):
            return cls.from_dict(data)
        else:
            # Fallback to direct instantiation if no from_dict method
            field_names = {field.name for field in cls.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in data.items() if k in field_names}
            return cls(**filtered_data)
    except Exception as e:
        if logger:
            logger.warning(f"Error creating {cls.__name__} from data: {e}")
            logger.debug(f"Data: {data}")
        raise


def setup_logging(log_level: str = "INFO") -> None:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"vibrent_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    ) 