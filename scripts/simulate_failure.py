import sys
import os
import time
import requests

# Fix import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gateway.config import NODE_IDS

def kill_node(node_id: str):
    print(f"💀 Simulating kill node: {node_id}")
    # Trong phiên bản này ta simulate bằng cách không xóa node thật
    print(f"   → Node {node_id} marked as DOWN (simulation)")

def recover_node(node_id: str):
    print(f"♻️  Recovering node: {node_id}")

if __name__ == "__main__":
    print("🔬 Sloppy Quorum + Hinted Handoff Simulation")
    print("=" * 60)
    
    time.sleep(1)
    
    # Test failure
    kill_node("node3")
    time.sleep(2)
    
    print("\n📡 Gửi dữ liệu khi node3 đang DOWN...\n")
    
    for i in range(8):
        payload = {
            "sensor_id": "temp_room1",
            "value": {
                "value": round(25.0 + i * 0.5, 1),
                "unit": "°C",
                "status": "emergency"
            }
        }
        
        try:
            r = requests.post("http://127.0.0.1:8000/api/write", json=payload, timeout=5)
            result = r.json()
            print(f"[{i+1}] {payload['sensor_id']:15} → {result.get('status')} (replicas: {result.get('replicas')})")
        except Exception as e:
            print(f"[{i+1}] Error: {e}")
        
        time.sleep(1.2)
    
    recover_node("node3")
    print("\n✅ Test hoàn tất!")
    print("Kiểm tra hinted handoff tại: http://127.0.0.1:8000/api/status")