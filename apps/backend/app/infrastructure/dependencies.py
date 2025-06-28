"""
Dependency injection container for the application
"""
from functools import lru_cache
from typing import Optional

from app.domain.repositories.contract_repository import ContractRepository


class DependencyContainer:
    """Container for managing application dependencies"""
    
    def __init__(self):
        self._contract_repository: Optional[ContractRepository] = None
    
    def get_contract_repository(self) -> ContractRepository:
        """Get contract repository instance"""
        if self._contract_repository is None:
            self._contract_repository = self._create_contract_repository()
        return self._contract_repository
    
    def _create_contract_repository(self) -> ContractRepository:
        """Create contract repository with Firebase fallback to mock"""
        try:
            # Try to create Firebase repository
            from app.infrastructure.persistence.firebase.contract_repository_impl import (
                FirebaseContractRepository,
                FIRESTORE_AVAILABLE
            )
            
            if FIRESTORE_AVAILABLE:
                repository = FirebaseContractRepository()
                print("✅ Using Firebase Contract Repository")
                return repository
            else:
                raise RuntimeError("Firestore not available")
                
        except Exception as e:
            print(f"⚠️ Firebase repository failed: {e}")
            print("🔄 Falling back to Mock Contract Repository")
            
            # Fallback to mock repository
            from app.infrastructure.persistence.mock_contract_repository import MockContractRepository
            return MockContractRepository()


# Global container instance
_container: Optional[DependencyContainer] = None


@lru_cache()
def get_dependency_container() -> DependencyContainer:
    """Get or create dependency container"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def get_contract_repository() -> ContractRepository:
    """FastAPI dependency for contract repository"""
    container = get_dependency_container()
    return container.get_contract_repository()