"""
Pure calculation functions for the drone pricing model.
"""

import math
from typing import List, Optional

from core.constants import WEIGHT_ADJUSTMENTS


# HULL
 
def hull_final_rate(hull_base_rate: float, weight_band: str) -> float:
    return hull_base_rate * WEIGHT_ADJUSTMENTS[weight_band]
 
def hull_premium(drone_value: float, hull_final_rate: float) -> float:
    return round(drone_value * hull_final_rate, 2)
 
# TPL
 
def riebesell(base_limit: float, z: float, x: float) -> float:
    return (x / base_limit) ** math.log2(1 + z)
 
def tpl_ilf(ilf_base_limit: float, ilf_z: float, tpl_excess: float, tpl_limit: float) -> float:
    return riebesell(ilf_base_limit, ilf_z, tpl_excess + tpl_limit) - riebesell(ilf_base_limit, ilf_z, tpl_excess)
 
def tpl_premium(drone_value: float, tpl_base_rate: float, tpl_ilf: float) -> float:
    return round(drone_value * tpl_base_rate * tpl_ilf, 2)
 
# DETACHABLE CAMERA
 
def camera_rate(drones: List[dict]) -> Optional[float]:
    eligible = [
        d["hull_final_rate"] for d in drones
        if d["has_detachable_camera"] and d["drone_value"] > 0
    ]
    return max(eligible) if eligible else None
 
def camera_premium(camera_rate: Optional[float], camera_value: float) -> Optional[float]:
    if camera_rate is None or camera_value == 0:
        return None
    return round(camera_value * camera_rate, 2)
 
# SUMMARY
 
def sum_premiums(premiums: List[Optional[float]]) -> float:
    return round(sum(p for p in premiums if p is not None), 2)
 
def sum_values(*values: Optional[float]) -> float:
    return round(sum(v for v in values if v is not None), 2)
 
def gross_premium(net_premium: float, brokerage: float) -> float:
    return round(net_premium / (1 - brokerage), 2)
 