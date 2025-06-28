"""
Converters for Firestore data types
"""
from datetime import datetime
from typing import Any, Dict, List, Union
import math
import json


def convert_firestore_document(data: Any) -> Any:
    """Convert Firestore objects to JSON serializable types"""
    if hasattr(data, 'timestamp'):  # Firestore timestamp
        return data.isoformat()
    elif hasattr(data, 'isoformat'):  # datetime object
        return data.isoformat()
    elif hasattr(data, 'path'):  # DocumentReference
        return data.path  # Convert to string path
    elif hasattr(data, 'latitude') and hasattr(data, 'longitude'):  # GeoPoint
        return {"latitude": data.latitude, "longitude": data.longitude}
    elif isinstance(data, dict):
        return {k: convert_firestore_document(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_firestore_document(item) for item in data]
    else:
        # Handle special numeric values
        if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
            return None  # Convert NaN and Infinity to null
        
        try:
            # Try to serialize the value - if it fails, convert to string
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            return str(data)


def parse_datetime(value: Any) -> datetime:
    """Parse various datetime formats to datetime object"""
    if isinstance(value, datetime):
        return value
    elif hasattr(value, 'timestamp'):  # Firestore timestamp
        return datetime.fromtimestamp(value.timestamp())
    elif isinstance(value, str):
        # Try to parse ISO format
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    elif isinstance(value, dict) and '_seconds' in value:
        # Firestore timestamp as dict
        return datetime.fromtimestamp(value['_seconds'])
    else:
        raise ValueError(f"Cannot parse datetime from: {value}")


def to_firestore_timestamp(dt: datetime):
    """Convert datetime to Firestore timestamp"""
    return dt