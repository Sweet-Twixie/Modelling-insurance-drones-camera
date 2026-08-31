"""
Raw constants for the drone pricing model
"""

BROKERAGE = 0.30
HULL_BASE_RATE = 0.06
TPL_BASE_RATE = 0.02
ILF_BASE_LIMIT = 1_000_000
ILF_Z = 0.2
MAX_DRONES_IN_AIR = 2
FLAT_DRONE_PREMIUM = 150
FLAT_CAMERA_PREMIUM = 50

WEIGHT_ADJUSTMENTS = {
    "0 - 5kg": 1.0,
    "5 - 10kg": 1.2,
    "10 - 20kg": 1.6,
    "> 20kg": 2.5,
}