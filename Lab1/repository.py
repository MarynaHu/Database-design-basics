from abc import ABC, abstractmethod
from typing import List, Optional
import json
import os
from models import Vehicle
import redis
import vehicle_pb2  # Згенерований файл
import psycopg2

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
        self._storage = {}
        self._current_id = 1

    def create(self, vehicle: Vehicle) -> Vehicle:
        vehicle.id = self._current_id
        self._storage[self._current_id] = vehicle
        self._current_id += 1
        return vehicle

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]:
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

class JsonVehicleRepository(VehicleRepository):
    def __init__(self, file_path: str = "vehicles.json"):
        self._file_path = file_path
        self._storage = {}
        self._current_id = 1
        self._load_from_disk()

    def _load_from_disk(self):
        """Зчитує дані з файлу при ініціалізації."""
        if not os.path.exists(self._file_path):
            return

        with open(self._file_path, 'r', encoding='utf-8') as f:
            try:
                data_list = json.load(f)
                for item in data_list:
                    vehicle = Vehicle(**item)
                    self._storage[vehicle.id] = vehicle
                
                # Відновлюємо лічильник ID, щоб не було конфліктів
                if self._storage:
                    self._current_id = max(self._storage.keys()) + 1
            except json.JSONDecodeError:
                pass # Файл порожній або пошкоджений

    def _save_to_disk(self):
        """Зберігає поточний стан словника у файл."""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            # Припускаємо, що vehicle.__dict__ повертає словник атрибутів (або використовуйте dataclasses.asdict(v))
            json.dump([v.__dict__ for v in self._storage.values()], f, indent=4, ensure_ascii=False)

    def create(self, vehicle: Vehicle) -> Vehicle:
        vehicle.id = self._current_id
        self._storage[self._current_id] = vehicle
        self._current_id += 1
        self._save_to_disk() # Додано збереження
        return vehicle

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]:
        all_vehicles = list(self._storage.values())
        return all_vehicles[offset: offset + limit]

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return self._storage.get(vehicle_id)

    def update(self, vehicle: Vehicle) -> Optional[Vehicle]:
        if vehicle.id in self._storage:
            self._storage[vehicle.id] = vehicle
            self._save_to_disk() # Додано збереження
            return vehicle
        return None

    def delete(self, vehicle_id: int) -> bool:
        if vehicle_id in self._storage:
            del self._storage[vehicle_id]
            self._save_to_disk() # Додано збереження
            return True
        return False

class RedisProtobufVehicleRepository(VehicleRepository):
    def __init__(self, host: str = 'localhost', port: int = 6379):
        # Підключення до Redis
        self._redis = redis.Redis(host=host, port=port, db=0)
        self._hash_key = "fleet:vehicles"
        self._id_counter_key = "fleet:vehicle_id_counter"

        # Ініціалізація лічильника ID, якщо база порожня
        if not self._redis.exists(self._id_counter_key):
            self._redis.set(self._id_counter_key, 0)

    def _vehicle_to_proto(self, vehicle: Vehicle) -> bytes:
        """Перетворює Python об'єкт у байти Protobuf."""
        proto_msg = vehicle_pb2.VehicleProto()
        proto_msg.id = vehicle.id
        proto_msg.make = vehicle.make
        proto_msg.model = vehicle.model
        proto_msg.license_plate = vehicle.license_plate
        
        return proto_msg.SerializeToString() # Серіалізація в байти

    def _proto_to_vehicle(self, proto_bytes: bytes) -> Vehicle:
        """Відновлює Python об'єкт з байтів Protobuf."""
        proto_msg = vehicle_pb2.VehicleProto()
        proto_msg.ParseFromString(proto_bytes)
        
        return Vehicle(
            id=proto_msg.id,
            make=proto_msg.make,
            model=proto_msg.model,
            year=2022, # Оскільки не додавали year у .proto файл, ставимо дефолтне значення
            license_plate=proto_msg.license_plate
        )

    def create(self, vehicle: Vehicle) -> Vehicle:
        # Атомарне збільшення ID в Redis
        new_id = self._redis.incr(self._id_counter_key)
        vehicle.id = new_id

        # Зберігаємо в Hash: ключ_хешу, поле(id), значення(байти)
        self._redis.hset(self._hash_key, str(new_id), self._vehicle_to_proto(vehicle))
        return vehicle

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]:
        # Отримуємо всі байти з Redis (повертає словник {id_bytes: proto_bytes})
        all_data = self._redis.hgetall(self._hash_key)
        
        vehicles = []
        for proto_bytes in all_data.values():
            vehicle = self._proto_to_vehicle(proto_bytes)
            # Якщо ви встановлюєте ID поза конструктором:
            # vehicle.id = int(vehicle_pb2.VehicleProto.FromString(proto_bytes).id)
            vehicles.append(vehicle)

        # Повертаємо з урахуванням пагінації
        return vehicles[offset: offset + limit]

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        proto_bytes = self._redis.hget(self._hash_key, str(vehicle_id))
        if proto_bytes:
            vehicle = self._proto_to_vehicle(proto_bytes)
            vehicle.id = vehicle_id
            return vehicle
        return None

    def update(self, vehicle: Vehicle) -> Optional[Vehicle]:
        # Перевіряємо, чи існує такий запис
        if self._redis.hexists(self._hash_key, str(vehicle.id)):
            self._redis.hset(self._hash_key, str(vehicle.id), self._vehicle_to_proto(vehicle))
            return vehicle
        return None

    def delete(self, vehicle_id: int) -> bool:
        # hdel повертає кількість видалених полів (1 - успіх, 0 - не знайдено)
        result = self._redis.hdel(self._hash_key, str(vehicle_id))
        return result > 0
    
class PostgresVehicleRepository(VehicleRepository):
    def __init__(self, connection_string: str):
        self._conn_str = connection_string

    def _get_connection(self):
        return psycopg2.connect(self._conn_str)

    def create(self, vehicle: Vehicle) -> Vehicle:
        # ДОДАНО: year у список колонок та %s у значення
        query = """
            INSERT INTO company_vehicles (make, model, license_plate, year) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # ДОДАНО: vehicle.year
                cursor.execute(query, (vehicle.make, vehicle.model, vehicle.license_plate, vehicle.year))
                
                vehicle.id = cursor.fetchone()[0]
                conn.commit()
                
        return vehicle

    def get_all(self, limit: int = 10, offset: int = 0) -> List[Vehicle]:
        # ДОДАНО: year у SELECT
        query = """
            SELECT id, make, model, license_plate, year 
            FROM company_vehicles 
            ORDER BY id 
            LIMIT %s OFFSET %s;
        """
        vehicles = []
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (limit, offset))
                
                for row in cursor.fetchall():
                    # ДОДАНО: year=row[4]
                    vehicle = Vehicle(id=row[0], make=row[1], model=row[2], license_plate=row[3], year=row[4])
                    vehicles.append(vehicle)
                    
        return vehicles

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        # ДОДАНО: year у SELECT
        query = "SELECT id, make, model, license_plate, year FROM company_vehicles WHERE id = %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (vehicle_id,))
                row = cursor.fetchone()
                
                if row:
                    # ДОДАНО: year=row[4]
                    vehicle = Vehicle(id=row[0], make=row[1], model=row[2], license_plate=row[3], year=row[4])
                    return vehicle
        return None

    def update(self, vehicle: Vehicle) -> Optional[Vehicle]:
        # ДОДАНО: year = %s
        query = """
            UPDATE company_vehicles 
            SET make = %s, model = %s, license_plate = %s, year = %s 
            WHERE id = %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                # ДОДАНО: vehicle.year
                cursor.execute(query, (vehicle.make, vehicle.model, vehicle.license_plate, vehicle.year, vehicle.id))
                
                if cursor.rowcount == 0:
                    return None
                conn.commit()
                
        return vehicle

    def delete(self, vehicle_id: int) -> bool:
        query = "DELETE FROM company_vehicles WHERE id = %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (vehicle_id,))
                success = cursor.rowcount > 0
                conn.commit()
                return success