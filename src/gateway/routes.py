from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import time

from src.gateway.config import N, W, R, NODE_IDS
from src.core.consistent_hash import HashRing
from src.node.node import Node
from src.core.vector_clock import VectorClock
from src.core.response import success_response

router = APIRouter()

# Cluster
nodes: Dict[str, Node] = {
    nid: Node(nid)
    for nid in NODE_IDS
}

hash_ring = HashRing(NODE_IDS)

# Simulate node failure
active_nodes = set(NODE_IDS)


class SensorData(BaseModel):
    sensor_id: str
    value: Dict[str, Any]

# WRITE
@router.post("/write", tags=["Data Operations"])
async def write_sensor(data: SensorData):

    key = f"{data.sensor_id}:{int(time.time() * 1000)}"

    clock = VectorClock()
    clock.increment("gateway")

    pref_list = hash_ring.get_preference_list(key, N)

    # Sloppy Quorum
    healthy_nodes = [
        nid
        for nid in pref_list
        if nid in active_nodes
    ]

    if len(healthy_nodes) < W:

        extra = [
            nid
            for nid in NODE_IDS
            if nid in active_nodes
            and nid not in healthy_nodes
        ]

        healthy_nodes.extend(
            extra[: W - len(healthy_nodes)]
        )

    successes = 0
    used_nodes = []

    # Write replicas
    for node_id in healthy_nodes[:W]:

        used_nodes.append(node_id)

        success = nodes[node_id].put(
            key,
            data.value,
            clock
        )

        if success:
            successes += 1

    # Hinted Handoff
    for orig_node in pref_list:

        if orig_node not in active_nodes:

            for temp_node in healthy_nodes[:W]:

                if temp_node != orig_node:

                    nodes[temp_node].store_hint(
                        orig_node,
                        key,
                        data.value,
                        clock
                    )

    # WRITE QUORUM CHECK
    if successes < W:

        raise HTTPException(
            status_code=503,
            detail=f"Write quorum failed. Required={W}, Got={successes}"
        )

    return success_response(
        "Write operation completed",
        {
            "status": "success",
            "key": key,
            "replicas": successes,
            "preferred_nodes": pref_list,
            "used_nodes": used_nodes,
            "down_nodes": [
                n
                for n in pref_list
                if n not in active_nodes
            ]
        }
    )


# READ
@router.get(
    "/read/{sensor_id}",
    tags=["Data Operations"]
)
async def read_sensor(sensor_id: str):

    all_versions = []

    for node in nodes.values():

        for k, (val, vc, ts) in node.store.items():

            if k.startswith(sensor_id + ":"):

                all_versions.append(
                    (k, val, vc, ts)
                )

    if not all_versions:

        raise HTTPException(
            status_code=404,
            detail="No data found"
        )

    all_versions.sort(
        key=lambda x: x[3],
        reverse=True
    )

    latest = all_versions[0]

    return success_response(
        "Latest sensor data retrieved",
        {
            "sensor_id": sensor_id,
            "latest_value": latest[1],
            "timestamp": latest[3],
            "vector_clock": latest[2].to_dict()
        }
    )


# STATUS
@router.get(
    "/status",
    tags=["Monitoring"]
)
async def cluster_status():

    # AUTO HINTED HANDOFF
    for target_node in active_nodes:

        for other_node in nodes.values():

            delivered = other_node.deliver_hints(
                target_node,
                nodes[target_node]
            )

            if delivered > 0:
                print(
                    f"[Auto Deliver] "
                    f"{delivered} hints -> {target_node}"
                )

    node_list = []

    active_count = 0
    total_records = 0
    total_hints = 0

    for nid, node in nodes.items():

        records = len(node.store)

        hints = sum(
            len(v)
            for v in node.hints.values()
        )

        online = nid in active_nodes

        if online:
            active_count += 1

        total_records += records
        total_hints += hints

        node_list.append({
            "node_id": nid,
            "online": online,
            "records": records,
            "hints": hints
        })

    return success_response(
        "Cluster status",
        {
            "summary": {
                "nodes": len(nodes),
                "active": active_count,
                "records": total_records,
                "hints": total_hints,
                "quorum": {
                    "N": N,
                    "W": W,
                    "R": R
                }
            },
            "nodes": node_list
        }
    )


# ADMIN
@router.post(
    "/admin/toggle_node/{node_id}",
    tags=["Admin"]
)
async def toggle_node(node_id: str):

    if node_id not in NODE_IDS:

        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    if node_id in active_nodes:

        active_nodes.remove(node_id)
        status = "DOWN"

    else:

        active_nodes.add(node_id)
        status = "UP"

        # Deliver hints
        for other_node in nodes.values():

            delivered = other_node.deliver_hints(
                node_id,
                nodes[node_id]
            )

            if delivered > 0:

                print(
                    f"[Hinted Handoff] Delivered "
                    f"{delivered} hints to {node_id}"
                )

    return success_response(
        f"Node {node_id} is now {status}",
        {
            "node": node_id,
            "status": status,
            "active_nodes": list(active_nodes)
        }
    )


# ROOT
@router.get("/", tags=["System"])
async def root():

    return success_response(
        "System is running",
        {
            "project": "IoT Sensor Hub",
            "replication": "Leaderless Replication",
            "features": [
                "Consistent Hashing",
                "Vector Clock",
                "Sloppy Quorum",
                "Hinted Handoff"
            ]
        }
    )