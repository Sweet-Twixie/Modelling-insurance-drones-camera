"""
The calculation graph ("functors") for the drone pricing model.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from core import library


@dataclass(frozen=True)
class Node:
    id: int
    deps: List[str]
    func: Callable[..., Any]   


NODES: Dict[str, Node] = {
    "hull_final_rate": Node(
        id=10,
        deps=["HULL_BASE_RATE", "weight_band"],
        func=library.hull_final_rate,
    ),
    "hull_premium": Node(
        id=11,
        deps=["drone_value", "hull_final_rate"],
        func=library.hull_premium,
    ),
    "tpl_ilf": Node(
        id=20,
        deps=["ILF_BASE_LIMIT", "ILF_Z", "tpl_excess", "tpl_limit"],
        func=library.tpl_ilf,
    ),
    "tpl_premium": Node(
        id=21,
        deps=["drone_value", "TPL_BASE_RATE", "tpl_ilf"],
        func=library.tpl_premium,
    ),
    "camera_rate": Node(
        id=30,
        deps=["drones"],
        func=library.camera_rate,
    ),
    "camera_premium": Node(
        id=31,
        deps=["camera_rate", "camera_value"],
        func=library.camera_premium,
    ),
    "net_drone_hull": Node(id=40, deps=["hull_premiums"], func=library.sum_premiums),
    "net_drone_tpl":  Node(id=41, deps=["tpl_premiums"], func=library.sum_premiums),
    "net_camera_hull":Node(id=42, deps=["camera_premiums"], func=library.sum_premiums),
    "net_total": Node(
        id=43,
        deps=["net_drone_hull", "net_drone_tpl", "net_camera_hull"],
        func=library.sum_values,
    ),
    "gross_drone_hull":  Node(id=50, deps=["net_drone_hull", "BROKERAGE"], func=library.gross_premium),
    "gross_drone_tpl":   Node(id=51, deps=["net_drone_tpl", "BROKERAGE"], func=library.gross_premium),
    "gross_camera_hull": Node(id=52, deps=["net_camera_hull", "BROKERAGE"], func=library.gross_premium),
    "gross_total":       Node(id=53, deps=["net_total", "BROKERAGE"], func=library.gross_premium),
}


def resolve(node_id: str, context: Dict[str, Any]) -> Any:
    """
    Resolve a Node's value by name, recursively resolving dependencies first.
    `context` holds raw constants + runtime inputs; resolved values are
    cached back into context as they're computed.
    """
    if node_id in context:
        return context[node_id]

    node = NODES[node_id]
    args = [resolve(dep, context) for dep in node.deps]
    value = node.func(*args)   # no globals() lookup needed -- func is already callable
    context[node_id] = value
    return value