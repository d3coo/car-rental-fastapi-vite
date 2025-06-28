"""
DateRange value object for handling date ranges
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    """Immutable value object representing a date range"""
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if self.end_date < self.start_date:
            raise ValueError("End date must be after or equal to start date")
    
    @property
    def duration_days(self) -> int:
        """Get duration in days"""
        return (self.end_date - self.start_date).days
    
    @property
    def duration_weeks(self) -> float:
        """Get duration in weeks"""
        return self.duration_days / 7
    
    @property
    def duration_months(self) -> float:
        """Get approximate duration in months (30 days)"""
        return self.duration_days / 30
    
    def contains(self, date: datetime) -> bool:
        """Check if a date is within this range"""
        return self.start_date <= date <= self.end_date
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another"""
        return (
            self.start_date <= other.end_date and 
            self.end_date >= other.start_date
        )
    
    def extend_to(self, new_end_date: datetime) -> 'DateRange':
        """Create new range extended to new end date"""
        if new_end_date <= self.end_date:
            raise ValueError("New end date must be after current end date")
        return DateRange(self.start_date, new_end_date)
    
    def shift(self, days: int) -> 'DateRange':
        """Shift the entire range by a number of days"""
        delta = timedelta(days=days)
        return DateRange(
            self.start_date + delta,
            self.end_date + delta
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'duration_days': self.duration_days
        }
    
    @classmethod
    def from_booking_type(
        cls, 
        start_date: datetime, 
        booking_type: str, 
        count: int = 1
    ) -> 'DateRange':
        """Create date range from booking type and count"""
        if booking_type == 'Day':
            end_date = start_date + timedelta(days=count)
        elif booking_type == 'Week':
            end_date = start_date + timedelta(weeks=count)
        elif booking_type == 'Month':
            end_date = start_date + timedelta(days=count * 30)
        else:
            raise ValueError(f"Invalid booking type: {booking_type}")
        
        return cls(start_date, end_date)
    
    def __str__(self) -> str:
        return f"{self.start_date.date()} to {self.end_date.date()} ({self.duration_days} days)"