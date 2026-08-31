"""
Quick smoke tests for every function in library.py.

Not pytest -- just plain asserts with print statements, so you can run it
directly (`python test_library.py`) and see PASS/FAIL for each function at a
glance. Expected values are taken from hand-calculated workbook figures
(drone AAA-111 / BBB-222 / CCC-333 from the original sample data).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from core import library
from core import constants, graph


 
def fmt(value):
    if isinstance(value, float):
        return round(value, 2)
    return value
 
def check(name, actual, expected, tol=1e-6):
    ok = (actual is None and expected is None) or (actual is not None and abs(actual - expected) < tol)
    print(f"{'PASS' if ok else 'FAIL':<5} {name:<30} got={fmt(actual)!r} expected={fmt(expected)!r}")
    assert ok, f"{name} failed"
 
 
# --- HULL ---
 
check("hull_final_rate (10-20kg)", library.hull_final_rate(0.05, "10 - 20kg"), 0.08)
check("hull_final_rate (>20kg)", library.hull_final_rate(0.05, "> 20kg"), 0.125)
check("hull_premium", library.hull_premium(8000, 0.08), 640.0)
 
# --- TPL / Riebesell (different base_limit and z this time) ---
 
exp = math.log2(1.25)
check("riebesell (at base)", library.riebesell(2_000_000, 0.25, 2_000_000), 1.0)
check("riebesell (at zero)", library.riebesell(2_000_000, 0.25, 0), 0.0)
check("riebesell (double base)", library.riebesell(2_000_000, 0.25, 4_000_000), 1.25)
 
check("tpl_ilf", library.tpl_ilf(2_000_000, 0.25, 2_000_000, 2_000_000), 0.25)
check("tpl_premium", library.tpl_premium(8000, 0.015, 1.0), 120.0)
 
# --- CAMERA -- mix of eligible/ineligible drones ---
 
drones = [
    {"hull_final_rate": 0.08, "has_detachable_camera": True, "drone_value": 8000},   # eligible
    {"hull_final_rate": 0.125, "has_detachable_camera": False, "drone_value": 9000}, # excluded: no camera
    {"hull_final_rate": 0.05, "has_detachable_camera": True, "drone_value": 0},      # excluded: zero value
]
check("camera_rate (mixed eligibility)", library.camera_rate(drones), 0.08)
check("camera_rate (empty list)", library.camera_rate([]), None)
 
check("camera_premium", library.camera_premium(0.08, 3000), 240.0)
check("camera_premium (no rate)", library.camera_premium(None, 3000), None)
check("camera_premium (zero value)", library.camera_premium(0.08, 0), None)
 
# --- SUMMARY ---
 
check("sum_premiums (with None)", library.sum_premiums([640, 120, None, 240]), 1000.0)
check("sum_premiums (all None)", library.sum_premiums([None, None]), 0.0)
check("sum_values (with None)", library.sum_values(1000, 200, None, 50), 1250.0)
check("gross_premium", library.gross_premium(1000, 0.25), 1333.33, tol=0.01)
 
# --- ENGINE (resolve, using actual constants: HULL_BASE_RATE=0.06, ILF_BASE_LIMIT=1e6, ILF_Z=0.2) ---
 
ctx = dict(vars(constants))
ctx.update({"weight_band": "> 20kg", "drone_value": 9000})
check("resolve(hull_premium)", graph.resolve("hull_premium", ctx), 1350.0)
 
ctx = dict(vars(constants))
ctx.update({"drone_value": 20000, "tpl_excess": 2_000_000, "tpl_limit": 3_000_000})
check("resolve(tpl_premium)", graph.resolve("tpl_premium", ctx), 130.82, tol=0.01)
 
print("\nAll checks passed.")
 