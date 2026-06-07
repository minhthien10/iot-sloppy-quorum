from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import time

from src.gateway.config import N, W, R, NODE_IDS
from src.core.consistent_hash import HashRing
from src.node.node import Node
from src.core.vector_clock import VectorClock

router = APIRouter()

# Khởi tạo nodes
nodes: Dict[str, Node] = {nid: Node(nid) for nid in NODE_IDS}
hash_ring = HashRing(NODE_IDS)

# Để simulate node failure
active_nodes = set(NODE_IDS)

class SensorData(BaseModel):
    sensor_id: str
    value: Dict[str, Any]

@router.post("/write")
async def write_sensor(data: SensorData):
    key = f"{data.sensor_id}:{int(time.time() * 1000)}"
    clock = VectorClock()
    clock.increment("gateway")

    pref_list = hash_ring.get_preference_list(key, N)
    
    # Sloppy Quorum: Xác định node healthy
    healthy_nodes = [nid for nid in pref_list if nid in active_nodes]
    
    if len(healthy_nodes) < W:
        extra = [nid for nid in NODE_IDS if nid in active_nodes and nid not in healthy_nodes]
        healthy_nodes.extend(extra[:W - len(healthy_nodes)])

    successes = 0
    used_nodes = []

    for node_id in healthy_nodes[:W]:
        used_nodes.append(node_id)
        success = nodes[node_id].put(key, data.value, clock)
        
        if success:
            successes += 1
        else:
            # Trường hợp hiếm: node từ chối ghi
            for orig in pref_list:
                if orig in active_nodes and orig != node_id:
                    nodes[node_id].store_hint(orig, key, data.value, clock)

    # === PHẦN QUAN TRỌNG: Hinted Handoff cho các node chính bị down ===
    for orig_node in pref_list:
        if orig_node not in active_nodes:                     # Node chính bị down
            for temp_node in healthy_nodes[:W]:
                if temp_node != orig_node:
                    nodes[temp_node].store_hint(orig_node, key, data.value, clock)

    status = "success" if successes >= W else "sloppy_quorum"
    
    return {
        "status": status, 
        "key": key, 
        "replicas": successes,
        "preferred_nodes": pref_list,
        "used_nodes": used_nodes,
        "down_nodes": [n for n in pref_list if n not in active_nodes]
    }

@router.get("/read/{sensor_id}")
async def read_sensor(sensor_id: str):
    all_versions = []
    for node in nodes.values():
        for k, (val, vc, ts) in node.store.items():
            if k.startswith(sensor_id + ":"):
                all_versions.append((k, val, vc, ts))

    if not all_versions:
        raise HTTPException(status_code=404, detail="No data found")

    all_versions.sort(key=lambda x: x[3], reverse=True)
    latest = all_versions[0]

    return {
        "sensor_id": sensor_id,
        "latest_value": latest[1],
        "timestamp": latest[3],
        "version": latest[2].to_dict()
    }

@router.get("/status")
async def cluster_status():
    """Trả về JSON sạch sẽ, dễ đọc"""
    status = {}
    total_records = 0
    total_hints = 0
    active_count = 0

    for nid, node in nodes.items():
        hints_count = sum(len(h) for h in node.hints.values())
        records = len(node.store)
        is_active = nid in active_nodes
        
        if is_active:
            active_count += 1
        
        total_records += records
        total_hints += hints_count
        
        status[nid] = {
            "status": "🟢 ONLINE" if is_active else "🔴 OFFLINE",
            "active": is_active,
            "records": records,
            "hints": hints_count
        }

    response = {
        "cluster": {
            "total_nodes": len(nodes),
            "active_nodes": active_count,
            "total_records": total_records,
            "total_hints": total_hints,
            "quorum": f"N={N}, W={W}, R={R}",
            "system_status": "✅ HEALTHY" if active_count >= W else "⚠️ DEGRADED"
        },
        "nodes": status
    }
    
    return response

# === API hỗ trợ test Sloppy Quorum ===
@router.post("/admin/toggle_node/{node_id}")
async def toggle_node(node_id: str):
    if node_id not in NODE_IDS:
        raise HTTPException(status_code=404, detail="Node not found")
    
    if node_id in active_nodes:
        active_nodes.remove(node_id)
        status = "DOWN"
    else:
        active_nodes.add(node_id)
        status = "UP"
        
        # Deliver hints khi node sống lại
        for other_node in nodes.values():
            delivered = other_node.deliver_hints(node_id, nodes[node_id])
            if delivered > 0:
                print(f"Delivered {delivered} hints to {node_id}")
    
    return {
        "node": node_id, 
        "status": status, 
        "active_nodes": list(active_nodes)
    }

@router.get("/")
async def root():
    return {"message": "IoT Sensor Hub - Leaderless Replication (Sloppy Quorum) is running!"}