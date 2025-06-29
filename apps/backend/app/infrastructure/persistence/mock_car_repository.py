"""
Mock implementation of Car repository for testing and fallback
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.domain.entities.car import Car, CarStatus, FuelType, TransmissionType
from app.domain.repositories.car_repository import CarRepository
from app.domain.value_objects.money import Money


class MockCarRepository(CarRepository):
    """Mock implementation of Car repository"""

    def __init__(self):
        self._cars: Dict[str, Car] = {}
        self._create_sample_data()

    def _create_sample_data(self):
        """Create sample cars for testing"""
        # Create sample cars
        sample_cars = [
            {
                "make": "Toyota",
                "model": "Camry",
                "year": 2023,
                "color": "White",
                "license_plate": "ABC-1234",
                "category": "Sedan",
                "daily_rate": Money(120, "SAR"),
                "weekly_rate": Money(700, "SAR"),
                "monthly_rate": Money(2500, "SAR"),
                "status": CarStatus.AVAILABLE,
                "location": "Riyadh Airport",
                "mileage": 15000,
                "fuel_type": FuelType.GASOLINE,
                "transmission": TransmissionType.AUTOMATIC,
                "seats": 5,
                "engine_size": "2.5L",
                "features": ["Air Conditioning", "Power Steering", "ABS"],
                "has_gps": True,
                "has_bluetooth": True,
                "has_usb_charger": True,
                "has_backup_camera": True,
            },
            {
                "make": "BMW",
                "model": "X5",
                "year": 2024,
                "color": "Black",
                "license_plate": "XYZ-5678",
                "category": "SUV",
                "daily_rate": Money(300, "SAR"),
                "weekly_rate": Money(1800, "SAR"),
                "monthly_rate": Money(7000, "SAR"),
                "status": CarStatus.AVAILABLE,
                "location": "Riyadh Downtown",
                "mileage": 5000,
                "fuel_type": FuelType.GASOLINE,
                "transmission": TransmissionType.AUTOMATIC,
                "seats": 7,
                "engine_size": "3.0L",
                "features": [
                    "Air Conditioning",
                    "Power Steering",
                    "ABS",
                    "Sunroof",
                    "Leather Seats",
                ],
                "has_gps": True,
                "has_bluetooth": True,
                "has_usb_charger": True,
                "has_backup_camera": True,
            },
            {
                "make": "Hyundai",
                "model": "Elantra",
                "year": 2022,
                "color": "Silver",
                "license_plate": "DEF-9876",
                "category": "Compact",
                "daily_rate": Money(80, "SAR"),
                "weekly_rate": Money(500, "SAR"),
                "monthly_rate": Money(1800, "SAR"),
                "status": CarStatus.RENTED,
                "location": "Jeddah Airport",
                "mileage": 25000,
                "fuel_type": FuelType.GASOLINE,
                "transmission": TransmissionType.MANUAL,
                "seats": 5,
                "engine_size": "1.6L",
                "features": ["Air Conditioning", "Power Steering"],
                "has_gps": False,
                "has_bluetooth": True,
                "has_usb_charger": False,
                "has_backup_camera": False,
            },
            {
                "make": "Tesla",
                "model": "Model 3",
                "year": 2024,
                "color": "Blue",
                "license_plate": "ELC-2024",
                "category": "Electric",
                "daily_rate": Money(250, "SAR"),
                "weekly_rate": Money(1500, "SAR"),
                "monthly_rate": Money(6000, "SAR"),
                "status": CarStatus.MAINTENANCE,
                "location": "Riyadh Downtown",
                "mileage": 8000,
                "fuel_type": FuelType.ELECTRIC,
                "transmission": TransmissionType.AUTOMATIC,
                "seats": 5,
                "features": ["Autopilot", "Premium Sound", "Heated Seats"],
                "has_gps": True,
                "has_bluetooth": True,
                "has_usb_charger": True,
                "has_backup_camera": True,
                "next_service_date": datetime.now() + timedelta(days=5),
            },
        ]

        for car_data in sample_cars:
            car = Car(**car_data)
            # Set ID manually after creation to avoid constructor issues
            car.id = f"car_{len(self._cars) + 1}"
            self._cars[car.id] = car

    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """Find car by ID"""
        return self._cars.get(car_id)

    async def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Find car by license plate"""
        for car in self._cars.values():
            if car.license_plate == license_plate:
                return car
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
        cars = list(self._cars.values())

        # Apply filters
        if status and status != "all":
            cars = [c for c in cars if c.status.value == status]

        if available_only:
            cars = [c for c in cars if c.is_available()]

        if category and category != "all":
            cars = [c for c in cars if c.category.lower() == category.lower()]

        if make and make != "all":
            cars = [c for c in cars if c.make.lower() == make.lower()]

        if location and location != "all":
            cars = [
                c for c in cars if c.location and c.location.lower() == location.lower()
            ]

        if search:
            search_lower = search.lower()
            cars = [
                c
                for c in cars
                if (
                    search_lower in c.make.lower()
                    or search_lower in c.model.lower()
                    or search_lower in c.license_plate.lower()
                    or search_lower in c.color.lower()
                    or search_lower in c.category.lower()
                    or search_lower in str(c.year)
                )
            ]

        # Sort by creation date (newest first)
        cars.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
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
        if not car.id or car.id == "new":
            car.id = f"car_{len(self._cars) + 1}"

        car.mark_updated()
        self._cars[car.id] = car
        return car

    async def delete(self, car_id: str) -> bool:
        """Delete car by ID"""
        if car_id in self._cars:
            del self._cars[car_id]
            return True
        return False

    async def count_by_status(self, status: str) -> int:
        """Count cars by status"""
        return len([c for c in self._cars.values() if c.status.value == status])

    async def find_available_cars(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Car]:
        """Find all available cars"""
        cars = [c for c in self._cars.values() if c.is_available()]

        if category:
            cars = [c for c in cars if c.category.lower() == category.lower()]

        if location:
            cars = [
                c for c in cars if c.location and c.location.lower() == location.lower()
            ]

        return cars

    async def find_cars_due_for_service(self, days_ahead: int = 7) -> List[Car]:
        """Find cars due for service within specified days"""
        future_date = datetime.now() + timedelta(days=days_ahead)
        return [
            c
            for c in self._cars.values()
            if (
                c.next_service_date
                and c.next_service_date <= future_date
                and c.status != CarStatus.OUT_OF_SERVICE
            )
        ]

    async def find_cars_by_make_and_model(self, make: str, model: str) -> List[Car]:
        """Find cars by make and model"""
        return [
            c
            for c in self._cars.values()
            if c.make.lower() == make.lower() and c.model.lower() == model.lower()
        ]
