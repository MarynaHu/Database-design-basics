from abc import ABC, abstractmethod
from typing import List, Optional
from models import Vehicle

class VehicleRepository(ABC):
    @abstractmethod
    def create(self, vehicle: Vehicle) -> Vehicle: pass
    
    @abstractmethod
    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]: pass
    
    @abstractmethod
    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]: pass
    
    @abstractmethod
    def update(self, vehicle: Vehicle) -> Optional[Vehicle]: pass
    
    @abstractmethod
    def delete(self, vehicle_id: int) -> bool: pass

class InMemoryVehicleRepository(VehicleRepository):
    def __init__(self):
        self._storage = {}  # dict, де ключ - це ID, а значення - об'єкт Vehicle
        self._current_id = 1

    def create(self, vehicle: Vehicle) -> Vehicle:
        vehicle.id = self._current_id
        self._storage[self._current_id] = vehicle
        self._current_id += 1
        return vehicle

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]:
        # Реалізація пейджингу (повертаємо шматок даних)
        all_vehicles = list(self._storage.values())
        return all_vehicles[offset: offset + limit]

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return self._storage.get(vehicle_id)

    def update(self, vehicle: Vehicle) -> Optional[Vehicle]:
        if vehicle.id in self._storage:
            self._storage[vehicle.id] = vehicle
            return vehicle
        return None

    def delete(self, vehicle_id: int) -> bool:
        if vehicle_id in self._storage:
            del self._storage[vehicle_id]
            return True
        return False