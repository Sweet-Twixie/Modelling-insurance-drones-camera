import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Customer, Drone, Camera
from core import library
from core import constants

customer = Customer(
    name="Acme Deliveries",
    max_drones_in_air=3,
    drones=[
        Drone("D001-754", "0 - 5kg", 3000, 2000000, 0, True),
        Drone("D002-242", "0 - 5kg", 24000, 5000000, 0, False),
        Drone("D003-532", "0 - 5kg", 3000, 500000, 0, True),
        Drone("D004-617", "0 - 5kg", 20000, 1000000, 1000000, True),
        Drone("D005-325", "> 20kg", 21000, 2000000, 0, True),
        Drone("D006-814", "> 20kg", 13000, 2000000, 0, True),
        Drone("D007-881", "10 - 20kg", 6000, 500000, 500000, True),
        Drone("D008-467", "10 - 20kg", 22000, 2000000, 0, False),
        Drone("D009-570", "0 - 5kg", 15000, 500000, 1000000, True),
        Drone("D010-949", "10 - 20kg", 21000, 1000000, 0, True),
    ],
)

customer.cameras = [
    Camera("C001-431", 1500),
    Camera("C002-504", 5500),
    Camera("C003-149", 1000),
    Camera("C004-940", 4750),
    Camera("C005-196", 3250),
    Camera("C006-696", 750),
    Camera("C007-619", 2000),
    Camera("C008-138", 1000),
    Camera("C009-544", 3750),
    Camera("C010-171", 2250),
    Camera("C011-192", 4750),
    Camera("C012-534", 750),
]

#  Extension 1: drones 

premiums = []

for drone in customer.drones:
    hull_final_rate = library.hull_final_rate(constants.HULL_BASE_RATE, drone.weight_band)
    hull_premium = library.hull_premium(drone.drone_value, hull_final_rate)
    tpl_ilf = library.tpl_ilf(constants.ILF_BASE_LIMIT, constants.ILF_Z, drone.tpl_excess, drone.tpl_limit)
    tpl_premium = library.tpl_premium(drone.drone_value, constants.TPL_BASE_RATE, tpl_ilf)

    premiums.append({
        "drone_id": drone.id,
        "hull_final_rate": hull_final_rate,                     
        "drone_value": drone.drone_value,                      
        "has_detachable_camera": drone.has_detachable_camera,  
        "total_premium": hull_premium + tpl_premium,
    })


ranked = sorted(premiums, key=lambda p: p["total_premium"], reverse=True)

for i, p in enumerate(ranked):
    charged = p["total_premium"] if i < customer.max_drones_in_air else constants.FLAT_DRONE_PREMIUM
    p["charged_premium"] = charged

print("Charged Premiums:")
for p in premiums:
    print(f"Drone {p['drone_id']}: £{p['charged_premium']:.2f}")


#  Extension 2: cameras 

drones_for_camera_rate = [
    {
        "hull_final_rate": p["hull_final_rate"],
        "has_detachable_camera": p["has_detachable_camera"],
        "drone_value": p["drone_value"],
    }
    for p in premiums
]
rate = library.camera_rate(drones_for_camera_rate)


more_cameras_than_drones = len(customer.cameras) > len(customer.drones)

camera_results = []
if more_cameras_than_drones:
    ranked_cameras = sorted(customer.cameras, key=lambda c: c.camera_value, reverse=True)
    for i, camera in enumerate(ranked_cameras):
        if i < customer.max_drones_in_air:
            charged = library.camera_premium(rate, camera.camera_value)
        else:
            charged = constants.FLAT_CAMERA_PREMIUM
        camera_results.append({"camera_id": camera.id, "charged_premium": charged})
else:
    for camera in customer.cameras:
        camera_results.append({
            "camera_id": camera.id,
            "charged_premium": library.camera_premium(rate, camera.camera_value),
        })

print("\nCharged Camera Premiums:")
for c in camera_results:
    print(f"Camera {c['camera_id']}: £{c['charged_premium']:.2f}")