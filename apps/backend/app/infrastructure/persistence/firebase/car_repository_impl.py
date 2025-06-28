"""
Firebase implementation of Car repository
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Try to import Firestore dependencies
    from google.cloud.firestore_v1 import FieldFilter

    FIRESTORE_AVAILABLE = True
    print("✅ Firestore imported successfully for Car repository")
except ImportError as e:
    FIRESTORE_AVAILABLE = False
    print(f"⚠️ Firestore dependencies not available for Car repository: {e}")

from app.domain.entities.car import Car, CarStatus, FuelType, TransmissionType
from app.domain.repositories.car_repository import CarRepository
from app.domain.value_objects.money import Money

if FIRESTORE_AVAILABLE:
    from ..converters import parse_datetime
    from .firebase_client import firebase_client


class FirebaseCarRepository(CarRepository):
    """Firebase implementation of Car repository"""

    def __init__(self):
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("Firestore dependencies not available")
        if not firebase_client.is_available:
            raise RuntimeError("Firebase client not initialized")
        self.collection = firebase_client.collection("Cars")

    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """Find car by ID"""
        doc = self.collection.document(car_id).get()
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Find car by license plate"""
        query = self.collection.where("license_plate", "==", license_plate).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
        make: Optional[str] = None,
        available_only: Optional[bool] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List cars with pagination and filters"""
        # Build query with database-level filters
        query = self._build_query(status, category, make, available_only, location)

        # Execute query and get documents
        docs = list(query.stream())
        cars = []

        # Process documents and apply client-side filters
        for doc in docs:
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if car and self._matches_filters(car, search):
                    cars.append(car)
            except Exception as e:
                print(f"Error processing car {doc.id}: {e}")
                continue

        # Apply pagination
        return self._paginate_results(cars, page, limit)

    def _build_query(
        self,
        status: Optional[str],
        category: Optional[str],
        make: Optional[str],
        available_only: Optional[bool],
        location: Optional[str],
    ):
        """Build Firestore query with database-level filters"""
        query = self.collection

        # Apply database-level filters
        if status and status != "all":
            query = query.where("status", "==", status)
        elif available_only:
            query = query.where("status", "==", "available")

        if category and category != "all":
            query = query.where("category", "==", category)

        if make and make != "all":
            query = query.where("make", "==", make)

        if location and location != "all":
            query = query.where("location", "==", location)

        # Fetch more than needed for client-side filtering
        query = query.limit(100)

        # Try to order by creation date
        try:
            query = query.order_by("created_at", direction="DESCENDING")
        except Exception:
            pass

        return query

    def _matches_filters(self, car: Car, search: Optional[str]) -> bool:
        """Check if car matches client-side filters"""
        if search:
            search_lower = search.lower()
            if not (
                search_lower in car.make.lower()
                or search_lower in car.model.lower()
                or search_lower in car.license_plate.lower()
                or search_lower in car.color.lower()
                or search_lower in car.category.lower()
                or search_lower in str(car.year)
            ):
                return False

        return True

    def _paginate_results(self, cars: List[Car], page: int, limit: int) -> Dict[str, Any]:
        """Apply pagination to filtered cars"""
        total = len(cars)
        offset = (page - 1) * limit
        paginated_cars = cars[offset : offset + limit]

        return {
            "cars": [c.to_dict() for c in paginated_cars],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit,
            "hasMore": page < (total + limit - 1) // limit,
        }

    async def save(self, car: Car) -> Car:
        """Save or update car"""
        data = self._from_entity(car)

        if car.id and car.id != "new":
            # Update existing
            self.collection.document(car.id).set(data)
        else:
            # Create new
            doc_ref = self.collection.add(data)[1]
            car.id = doc_ref.id

        return car

    async def delete(self, car_id: str) -> bool:
        """Delete car by ID"""
        try:
            self.collection.document(car_id).delete()
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count cars by status"""
        query = self.collection.where("status", "==", status)
        return len(list(query.stream()))

    async def find_available_cars(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Car]:
        """Find all available cars"""
        query = self.collection.where("status", "==", "available")

        if category:
            query = query.where("category", "==", category)

        if location:
            query = query.where("location", "==", location)

        cars = []
        for doc in query.stream():
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if car:
                    cars.append(car)
            except Exception:
                continue

        return cars

    async def find_cars_due_for_service(self, days_ahead: int = 7) -> List[Car]:
        """Find cars due for service within specified days"""
        future_date = datetime.now() + timedelta(days=days_ahead)
        
        # Since Firestore has limited date comparison, we'll fetch all cars
        # and filter client-side
        query = self.collection.limit(1000)  # Reasonable limit
        cars = []

        for doc in query.stream():
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if (car and car.next_service_date 
                    and car.next_service_date <= future_date
                    and car.status != CarStatus.OUT_OF_SERVICE):
                    cars.append(car)
            except Exception:
                continue

        return cars

    async def find_cars_by_make_and_model(
        self, make: str, model: str
    ) -> List[Car]:
        """Find cars by make and model"""
        query = self.collection.where("make", "==", make).where("model", "==", model)
        cars = []

        for doc in query.stream():
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if car:
                    cars.append(car)
            except Exception:
                continue

        return cars

    def _to_entity(self, doc_id: str, data: Dict[str, Any]) -> Optional[Car]:
        """Convert Firestore document to Car entity"""
        try:
            # Parse money values
            daily_rate = Money(
                data.get("daily_rate", 0), 
                data.get("currency", "SAR")
            )
            
            weekly_rate = None
            if data.get("weekly_rate"):
                weekly_rate = Money(
                    data.get("weekly_rate"),
                    data.get("currency", "SAR")
                )

            monthly_rate = None
            if data.get("monthly_rate"):
                monthly_rate = Money(
                    data.get("monthly_rate"),
                    data.get("currency", "SAR")
                )

            # Parse enums safely
            status = CarStatus.AVAILABLE
            if data.get("status") and data.get("status") in [s.value for s in CarStatus]:
                status = CarStatus(data.get("status"))

            fuel_type = None
            if data.get("fuel_type") and data.get("fuel_type") in [f.value for f in FuelType]:
                fuel_type = FuelType(data.get("fuel_type"))

            transmission = None
            if data.get("transmission") and data.get("transmission") in [t.value for t in TransmissionType]:
                transmission = TransmissionType(data.get("transmission"))

            # Parse dates
            last_service_date = None
            if data.get("last_service_date"):
                last_service_date = parse_datetime(data["last_service_date"])

            next_service_date = None
            if data.get("next_service_date"):
                next_service_date = parse_datetime(data["next_service_date"])

            # Create entity with defaults for missing data (backward compatibility)
            car = Car(
                make=data.get("make", ""),
                model=data.get("model", ""),
                year=data.get("year", datetime.now().year),
                color=data.get("color", ""),
                license_plate=data.get("license_plate", ""),
                category=data.get("category", ""),
                daily_rate=daily_rate,
                weekly_rate=weekly_rate,
                monthly_rate=monthly_rate,
                status=status,
                location=data.get("location"),
                mileage=data.get("mileage"),
                fuel_type=fuel_type,
                transmission=transmission,
                seats=data.get("seats"),
                engine_size=data.get("engine_size"),
                features=data.get("features", []),
                has_gps=data.get("has_gps", False),
                has_bluetooth=data.get("has_bluetooth", False),
                has_usb_charger=data.get("has_usb_charger", False),
                has_backup_camera=data.get("has_backup_camera", False),
                last_service_date=last_service_date,
                next_service_date=next_service_date,
                service_interval_km=data.get("service_interval_km"),
                car_data=data.get("car_data", {}),
            )

            # Set the document ID and timestamps manually after creation
            car.id = doc_id
            if data.get("created_at"):
                car.created_at = parse_datetime(data["created_at"])
            if data.get("updated_at"):
                car.updated_at = parse_datetime(data["updated_at"])

            return car

        except Exception as e:
            print(f"Error converting document to Car entity: {e}")
            return None

    def _from_entity(self, car: Car) -> Dict[str, Any]:
        """Convert Car entity to Firestore document"""
        data = car.to_dict()

        # Convert datetime objects for Firestore
        data["created_at"] = car.created_at
        data["updated_at"] = car.updated_at
        
        if car.last_service_date:
            data["last_service_date"] = car.last_service_date
        if car.next_service_date:
            data["next_service_date"] = car.next_service_date

        # Remove the id field as it's the document ID
        data.pop("id", None)
        # Remove computed fields
        data.pop("display_name", None)
        data.pop("age_years", None)
        data.pop("is_new", None)
        data.pop("is_available", None)
        data.pop("is_overdue_for_service", None)

        return data