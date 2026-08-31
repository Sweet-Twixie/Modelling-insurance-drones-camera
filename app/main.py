import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from core import constants
from core import library
from core import graph

def get_example_data():
    example_data = { 
        "insured": "Drones R Us",
        "underwriter": "Michael",
        "broker": "AON",
        "brokerage": 0.3,
        "max_drones_in_air": 2,
        "drones": [
            {
                "serial_number": "AAA-111",
                "value": 10000,
                "weight": "0 - 5kg",
                "has_detachable_camera": True,
                "tpl_limit": 1_000_000,  
                "tpl_excess": 0,         
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            },
            {
                "serial_number": "BBB-222",
                "value": 12000,
                "weight": "10 - 20kg",
                "has_detachable_camera": False,
                "tpl_limit": 4_000_000,
                "tpl_excess": 1_000_000,
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            },
            {
                "serial_number": "AAA-123",
                "value": 15000,
                "weight": "5 - 10kg",
                "has_detachable_camera": True,
                "tpl_limit": 5_000_000,
                "tpl_excess": 5_000_000,
                "hull_base_rate": None,
                "hull_weight_adjustment": None,
                "hull_final_rate": None,
                "hull_premium": None,
                "tpl_base_rate": None,
                "tpl_base_layer_premium": None,
                "tpl_ilf": None,
                "tpl_layer_premium": None
            }
        ],
        "detachable_cameras": [
            {"serial_number": "ZZZ-999", "value": 5000, "hull_rate": None, "hull_premium": None},
            {"serial_number": "YYY-888", "value": 2500, "hull_rate": None, "hull_premium": None},
            {"serial_number": "XXX-777", "value": 1500, "hull_rate": None, "hull_premium": None},
            {"serial_number": "WWW-666", "value": 2000, "hull_rate": None, "hull_premium": None}
        ],
        "gross_prem": {
            "drones_hull": None,
            "drones_tpl": None,
            "cameras_hull": None,
            "total": None
        },
        "net_prem": {
            "drones_hull": None,
            "drones_tpl": None,
            "cameras_hull": None,
            "total": None
        }
    }

    return example_data


HULL_BASE_RATE = constants.HULL_BASE_RATE
TPL_BASE_RATE = constants.TPL_BASE_RATE
ILF_BASE_LIMIT = constants.ILF_BASE_LIMIT
ILF_Z = constants.ILF_Z

def main():
    """
    Perform the rating calculations replicating the Excel model.
    """

    model_data = get_example_data()

    #  Drones: hull + TPL, one drone at a time 
    for drone in model_data["drones"]:
        drone["hull_base_rate"] = HULL_BASE_RATE
        drone["hull_final_rate"] = library.hull_final_rate(HULL_BASE_RATE, drone["weight"])
        drone["hull_weight_adjustment"] = drone["hull_final_rate"] / HULL_BASE_RATE
        drone["hull_premium"] = library.hull_premium(drone["value"], drone["hull_final_rate"])

        drone["tpl_base_rate"] = TPL_BASE_RATE
        drone["tpl_base_layer_premium"] = drone["value"] * TPL_BASE_RATE
        drone["tpl_ilf"] = library.tpl_ilf(ILF_BASE_LIMIT, ILF_Z, drone["tpl_excess"], drone["tpl_limit"])
        drone["tpl_layer_premium"] = library.tpl_premium(drone["value"], TPL_BASE_RATE, drone["tpl_ilf"])

    #  Cameras: shared rate = highest hull_final_rate among eligible drones
    eligible_drones = [
        {
            "hull_final_rate": d["hull_final_rate"],
            "has_detachable_camera": d["has_detachable_camera"],
            "drone_value": d["value"],
        }
        for d in model_data["drones"]
    ]
    rate = library.camera_rate(eligible_drones)

    for camera in model_data["detachable_cameras"]:
        camera["hull_rate"] = rate
        camera["hull_premium"] = library.camera_premium(rate, camera["value"])

    #  Premium summary: net, then gross via brokerage 
    brokerage = model_data["brokerage"]

    net_drones_hull = library.sum_premiums([d["hull_premium"] for d in model_data["drones"]])
    net_drones_tpl = library.sum_premiums([d["tpl_layer_premium"] for d in model_data["drones"]])
    net_cameras_hull = library.sum_premiums([c["hull_premium"] for c in model_data["detachable_cameras"]])
    net_total = library.sum_values(net_drones_hull, net_drones_tpl, net_cameras_hull)

    model_data["net_prem"]["drones_hull"] = net_drones_hull
    model_data["net_prem"]["drones_tpl"] = net_drones_tpl
    model_data["net_prem"]["cameras_hull"] = net_cameras_hull
    model_data["net_prem"]["total"] = net_total

    model_data["gross_prem"]["drones_hull"] = library.gross_premium(net_drones_hull, brokerage)
    model_data["gross_prem"]["drones_tpl"] = library.gross_premium(net_drones_tpl, brokerage)
    model_data["gross_prem"]["cameras_hull"] = library.gross_premium(net_cameras_hull, brokerage)
    model_data["gross_prem"]["total"] = library.gross_premium(net_total, brokerage)

    return model_data


if __name__ == "__main__":
    import json
    result = main()
    print(json.dumps(result, indent=2))