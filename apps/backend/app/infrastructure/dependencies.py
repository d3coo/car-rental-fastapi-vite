"""
Dependency injection container for the application
"""

from functools import lru_cache
from typing import Optional

from app.domain.repositories.contract_repository import ContractRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.car_repository import CarRepository


class DependencyContainer:
    """Container for managing application dependencies"""

    def __init__(self):
        self._contract_repository: Optional[ContractRepository] = None
        self._user_repository: Optional[UserRepository] = None
        self._car_repository: Optional[CarRepository] = None

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
                FIRESTORE_AVAILABLE,
                FirebaseContractRepository,
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
            from app.infrastructure.persistence.mock_contract_repository import (
                MockContractRepository,
            )

            return MockContractRepository()

    def get_user_repository(self) -> UserRepository:
        """Get user repository instance"""
        if self._user_repository is None:
            self._user_repository = self._create_user_repository()
        return self._user_repository

    def _create_user_repository(self) -> UserRepository:
        """Create user repository with Firebase fallback to mock"""
        try:
            # Try to create Firebase repository
            from app.infrastructure.persistence.firebase.user_repository_impl import (
                FIRESTORE_AVAILABLE,
                FirebaseUserRepository,
            )

            if FIRESTORE_AVAILABLE:
                repository = FirebaseUserRepository()
                print("✅ Using Firebase User Repository")
                return repository
            else:
                raise RuntimeError("Firestore not available")

        except Exception as e:
            print(f"⚠️ Firebase user repository failed: {e}")
            print("🔄 Falling back to Mock User Repository")

            # Fallback to mock repository
            from app.infrastructure.persistence.mock_user_repository import (
                MockUserRepository,
            )

            return MockUserRepository()

    def get_car_repository(self) -> CarRepository:
        """Get car repository instance"""
        if self._car_repository is None:
            self._car_repository = self._create_car_repository()
        return self._car_repository

    def _create_car_repository(self) -> CarRepository:
        """Create car repository with Firebase fallback to mock"""
        try:
            # Try to create Firebase repository
            from app.infrastructure.persistence.firebase.car_repository_impl import (
                FIRESTORE_AVAILABLE,
                FirebaseCarRepository,
            )

            if FIRESTORE_AVAILABLE:
                repository = FirebaseCarRepository()
                print("✅ Using Firebase Car Repository")
                return repository
            else:
                raise RuntimeError("Firestore not available")

        except Exception as e:
            print(f"⚠️ Firebase car repository failed: {e}")
            print("🔄 Falling back to Mock Car Repository")

            # Fallback to mock repository
            from app.infrastructure.persistence.mock_car_repository import (
                MockCarRepository,
            )

            return MockCarRepository()


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


def get_user_repository() -> UserRepository:
    """FastAPI dependency for user repository"""
    container = get_dependency_container()
    return container.get_user_repository()


def get_car_repository() -> CarRepository:
    """FastAPI dependency for car repository"""
    container = get_dependency_container()
    return container.get_car_repository()
