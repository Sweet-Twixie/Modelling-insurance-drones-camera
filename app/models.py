from dataclasses import dataclass, field
from typing import List


@dataclass
class Drone:
    id: str
    weight_band: str
    drone_value: float
    tpl_limit: float
    tpl_excess: float
    has_detachable_camera: bool


@dataclass
class Camera:
    id: str
    camera_value: float


@dataclass
class Customer:
    name: str
    max_drones_in_air: int          # "n"
    drones: List[Drone] = field(default_factory=list)
    cameras: List[Camera] = field(default_factory=list)