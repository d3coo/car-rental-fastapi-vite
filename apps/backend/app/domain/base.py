"""
Base classes for domain entities and value objects
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


@dataclass
class Entity(ABC):
    """Base class for all domain entities"""
    # These fields will be added by __post_init__ to avoid ordering issues
    id: str = field(default='', init=False)
    created_at: datetime = field(default_factory=datetime.now, init=False)
    updated_at: datetime = field(default_factory=datetime.now, init=False)
    
    def __post_init__(self):
        """Called after initialization"""
        if not self.id or self.id == 'new' or self.id == '':
            self.id = str(uuid.uuid4())
        if not hasattr(self, 'created_at') or not self.created_at:
            self.created_at = datetime.now()
        if not hasattr(self, 'updated_at') or not self.updated_at:
            self.updated_at = datetime.now()
    
    def mark_updated(self):
        """Mark entity as updated"""
        self.updated_at = datetime.now()
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        pass
    
    def __eq__(self, other):
        """Entities are equal if they have the same ID"""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Hash based on ID"""
        return hash(self.id)


@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for all value objects"""
    
    def __post_init__(self):
        """Validate value object after creation"""
        self.validate()
    
    @abstractmethod
    def validate(self):
        """Validate the value object"""
        pass


class DomainException(Exception):
    """Base exception for domain errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__


class ValidationError(DomainException):
    """Raised when domain validation fails"""
    pass


class BusinessRuleViolation(DomainException):
    """Raised when business rules are violated"""
    pass


class EntityNotFound(DomainException):
    """Raised when an entity is not found"""
    pass