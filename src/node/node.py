import json
import os
import time
from collections import defaultdict
from src.core.vector_clock import VectorClock
from src.config import DATA_DIR

class Node:
    def __init__(self, node_id: str):
        self.id = node_id
        self.store = {}                    
        self.hints = defaultdict(list)    
        
        self.db_file = os.path.join(DATA_DIR, f"{node_id}_db.json")
        self.hints_file = os.path.join(DATA_DIR, f"{node_id}_hints.json")
        self.load_data()

    def load_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # Load DB
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        vc = VectorClock.from_dict(v.get('clock'))
                        self.store[k] = (v['value'], vc, v['timestamp'])
            except:
                pass

        # Load Hints
        if os.path.exists(self.hints_file):
            try:
                with open(self.hints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for target, hint_list in data.items():
                        for h in hint_list:
                            vc = VectorClock.from_dict(h.get('clock'))
                            self.hints[target].append((h['key'], h['value'], vc, h['timestamp']))
            except:
                pass

    def save_data(self):
        # Save DB
        db_data = {}
        for k, (val, vc, ts) in self.store.items():
            db_data[k] = {
                "value": val,
                "clock": vc.to_dict(),
                "timestamp": ts
            }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)

        # Save Hints
        hints_data = {}
        for target, hint_list in self.hints.items():
            hints_data[target] = []
            for key, val, vc, ts in hint_list:
                hints_data[target].append({
                    "key": key,
                    "value": val,
                    "clock": vc.to_dict(),
                    "timestamp": ts
                })
        with open(self.hints_file, 'w', encoding='utf-8') as f:
            json.dump(hints_data, f, ensure_ascii=False, indent=2)

    def put(self, key: str, value: dict, clock: VectorClock):
        current = self.store.get(key)
        if current and current[1] > clock:   
            return False  

        self.store[key] = (value, clock, time.time())
        self.save_data()
        return True

    def get(self, key: str):
        return self.store.get(key)

    def store_hint(self, target_node: str, key: str, value: dict, clock: VectorClock):
        self.hints[target_node].append((key, value, clock, time.time()))
        self.save_data()

    def deliver_hints(self, target_node: str, target_node_obj):
        """Gửi hints sang node đích khi node đó online"""
        if target_node not in self.hints:
            return 0
        
        delivered = 0
        remaining = []
        
        for item in self.hints[target_node]:
            key, value, clock, _ = item
            if target_node_obj.put(key, value, clock):
                delivered += 1
            else:
                remaining.append(item)
        
        self.hints[target_node] = remaining
        if delivered > 0:
            self.save_data()
        return delivered