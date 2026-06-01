from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicle:
    id: Optional[int]
    make: str
    model: str
    license_plate: str
    year: int