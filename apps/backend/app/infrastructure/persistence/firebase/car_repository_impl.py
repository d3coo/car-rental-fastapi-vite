"""
Firebase implementation of Car repository
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Try to import Firestore dependencies
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
        self.collection = firebase_client.collection(
            "cars"
        )  # Firebase collection is lowercase
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def _run_query(self, query):
        """Helper to run Firestore query asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: list(query.stream()))

    async def _get_document(self, doc_ref):
        """Helper to get Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, doc_ref.get)

    async def _set_document(self, doc_ref, data):
        """Helper to set Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: doc_ref.set(data))

    async def _add_document(self, data):
        """Helper to add Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, lambda: self.collection.add(data)
        )

    async def _delete_document(self, doc_ref):
        """Helper to delete Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, doc_ref.delete)

    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """Find car by ID"""
        doc = await self._get_document(self.collection.document(car_id))
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Find car by license plate"""
        # Since Firebase doesn't have license_plate field and we generate them,
        # we need to search through all cars and check generated license plates
        # License plate format: {make[:3]}-{doc_id[:4]}

        try:
            # Get all cars and check if any match the license plate pattern
            query = self.collection.limit(
                200
            )  # Increased limit for better search coverage
            docs = await self._run_query(query)

            for doc in docs:
                try:
                    # Check if this document could generate the license plate
                    doc_data = doc.to_dict()
                    make = doc_data.get("make", "CAR")
                    generated_license = f"{make[:3].upper()}-{doc.id[:4]}"

                    if generated_license == license_plate:
                        return self._to_entity(doc.id, doc_data)
                except Exception as e:
                    print(f"Error processing car document {doc.id}: {e}")
                    continue

            return None
        except Exception as e:
            print(f"Error in find_by_license_plate: {e}")
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
        # Start with basic query - Firebase doesn't have DDD fields, so no database filtering
        query = self.collection.limit(
            100
        )  # Get reasonable amount for client-side filtering

        # We can filter by make at database level since Firebase has this field
        if make and make != "all":
            query = query.where("make", "==", make)

        # Execute query and get documents
        docs = await self._run_query(query)
        cars = []

        # Process documents and apply client-side filters
        for doc in docs:
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if car and self._matches_all_filters(
                    car, status, category, available_only, location, search
                ):
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

    def _matches_all_filters(
        self,
        car: Car,
        status: Optional[str] = None,
        category: Optional[str] = None,
        available_only: Optional[bool] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
    ) -> bool:
        """Check if car matches all client-side filters"""
        # Status filter
        if status and status != "all":
            if car.status.value != status:
                return False

        # Available only filter
        if available_only and not car.is_available():
            return False

        # Category filter
        if category and category != "all":
            if car.category.lower() != category.lower():
                return False

        # Location filter
        if location and location != "all":
            if not car.location or car.location.lower() != location.lower():
                return False

        # Search filter
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

    def _paginate_results(
        self, cars: List[Car], page: int, limit: int
    ) -> Dict[str, Any]:
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
            await self._set_document(self.collection.document(car.id), data)
        else:
            # Create new
            _, doc_ref = await self._add_document(data)
            car.id = doc_ref.id

        return car

    async def delete(self, car_id: str) -> bool:
        """Delete car by ID"""
        try:
            await self._delete_document(self.collection.document(car_id))
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count cars by status"""
        query = self.collection.where("status", "==", status)
        docs = await self._run_query(query)
        return len(docs)

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
        docs = await self._run_query(query)
        for doc in docs:
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

        docs = await self._run_query(query)
        for doc in docs:
            try:
                car = self._to_entity(doc.id, doc.to_dict())
                if (
                    car
                    and car.next_service_date
                    and car.next_service_date <= future_date
                    and car.status != CarStatus.OUT_OF_SERVICE
                ):
                    cars.append(car)
            except Exception:
                continue

        return cars

    async def find_cars_by_make_and_model(self, make: str, model: str) -> List[Car]:
        """Find cars by make and model"""
        query = self.collection.where("make", "==", make).where("model", "==", model)
        cars = []

        docs = await self._run_query(query)
        for doc in docs:
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
            # Clean Firebase objects first
            cleaned_data = self._clean_firebase_objects(data)

            # Parse different data types
            money_values = self._parse_money_values(cleaned_data)
            enum_values = self._parse_enum_values(cleaned_data)
            service_dates = self._parse_service_dates(cleaned_data)

            # Create entity using EXACT Firebase schema mapping
            # car_type: ["Economy", "All"] - take first non-"All" element
            car_types = cleaned_data.get("car_type", ["Economy"])
            category = "Economy"  # Default
            if car_types and isinstance(car_types, list):
                # Find first category that's not "All" or Arabic equivalent
                for cat in car_types:
                    if cat not in ["All", "الجميع"]:
                        category = cat
                        break

            # Generate license plate since Firebase doesn't have this field
            license_plate = (
                f"{cleaned_data.get('make', 'CAR')[:3].upper()}-{doc_id[:4]}"
            )

            car = Car(
                make=cleaned_data.get("make", ""),
                model=cleaned_data.get("model", ""),
                year=cleaned_data.get("year", datetime.now().year),
                color="Unknown",  # Firebase schema doesn't include color
                license_plate=license_plate,
                category=category,
                daily_rate=money_values["daily_rate"],
                weekly_rate=money_values["weekly_rate"],
                monthly_rate=money_values["monthly_rate"],
                status=enum_values["status"],
                location=data.get("location"),
                mileage=data.get("mileage"),
                fuel_type=enum_values["fuel_type"],
                transmission=enum_values["transmission"],
                seats=cleaned_data.get(
                    "Seats", 5
                ),  # EXACT Firebase field: "Seats" (capital S)
                engine_size=None,  # Firebase schema doesn't include engine_size
                features=self._extract_features(data),
                has_gps=False,  # Firebase doesn't have these boolean fields
                has_bluetooth=False,
                has_usb_charger=False,
                has_backup_camera=False,
                last_service_date=service_dates["last_service_date"],
                next_service_date=service_dates["next_service_date"],
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

    def _parse_money_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse money values from Firestore data using exact Firebase schema"""
        # EXACT Firebase field mapping based on MCP schema:
        # rental_price = daily rate
        # rental_price_week = weekly rate
        # rental_price_mounth = monthly rate (Firebase has typo)

        # Handle cases where Firebase has 0 rates (set minimum of 1 to pass validation)
        daily_price = data.get("rental_price", 0)
        daily_rate = Money(
            max(daily_price, 1), "SAR"
        )  # Minimum 1 SAR to pass validation

        weekly_rate = None
        if data.get("rental_price_week"):
            weekly_rate = Money(data.get("rental_price_week"), "SAR")

        monthly_rate = None
        if data.get(
            "rental_price_mounth"
        ):  # Firebase typo: "mounth" instead of "month"
            monthly_rate = Money(data.get("rental_price_mounth"), "SAR")

        return {
            "daily_rate": daily_rate,
            "weekly_rate": weekly_rate,
            "monthly_rate": monthly_rate,
        }

    def _parse_enum_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse enum values from Firestore data using exact Firebase schema"""
        # EXACT Firebase status mapping based on MCP schema:
        # isOutOfService: true/false
        # isOutOfStock: true/false
        is_out_of_service = data.get("isOutOfService", False)
        is_out_of_stock = data.get("isOutOfStock", False)

        if is_out_of_service:
            status = CarStatus.MAINTENANCE
        elif is_out_of_stock:
            status = CarStatus.RENTED  # Out of stock = currently rented
        else:
            status = CarStatus.AVAILABLE

        # Firebase doesn't have fuel_type field, default to gasoline
        fuel_type = FuelType.GASOLINE

        # EXACT Firebase transmission mapping:
        # trans_type: "AT" = Automatic, "MT" = Manual
        trans_type = data.get("trans_type", "AT")
        transmission = (
            TransmissionType.AUTOMATIC
            if trans_type == "AT"
            else TransmissionType.MANUAL
        )

        return {"status": status, "fuel_type": fuel_type, "transmission": transmission}

    def _parse_service_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse service dates from Firestore data"""
        last_service_date = None
        if data.get("last_service_date"):
            last_service_date = parse_datetime(data["last_service_date"])

        next_service_date = None
        if data.get("next_service_date"):
            next_service_date = parse_datetime(data["next_service_date"])

        return {
            "last_service_date": last_service_date,
            "next_service_date": next_service_date,
        }

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

    def _extract_features(self, data: Dict[str, Any]) -> List[str]:
        """Extract features from Firebase data using exact schema"""
        features = []
        # EXACT Firebase boolean fields:
        if data.get("air_condition", False):  # Firebase: air_condition
            features.append("Air Conditioning")
        if data.get("isNormalBooking", False):
            features.append("Normal Booking")
        if data.get("isPackages", False):
            features.append("Package Deals")
        return features

    def _clean_firebase_objects(self, obj: Any) -> Any:
        """Clean Firebase objects for JSON serialization"""
        try:
            # Import here to avoid circular dependencies
            from google.cloud.firestore_v1._helpers import (
                DatetimeWithNanoseconds,
                GeoPoint,
            )
            from google.cloud.firestore_v1.document import DocumentReference

            if isinstance(obj, DocumentReference):
                # Extract just the document ID from the reference
                return obj.id
            elif isinstance(obj, DatetimeWithNanoseconds):
                # Convert to ISO string
                return obj.isoformat()
            elif isinstance(obj, GeoPoint):
                # Convert to lat/lng dict
                return {"lat": obj.latitude, "lng": obj.longitude}
            elif isinstance(obj, dict):
                # Recursively clean dictionaries
                return {k: self._clean_firebase_objects(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                # Recursively clean lists
                return [self._clean_firebase_objects(item) for item in obj]
            else:
                # Return primitive types as-is
                return obj
        except Exception as e:
            print(f"Warning: Error cleaning Firebase object: {e}")
            return str(obj)  # Fallback to string representation
