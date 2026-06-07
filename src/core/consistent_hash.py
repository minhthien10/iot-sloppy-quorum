import hashlib
import bisect

class HashRing:
    def __init__(self, nodes: list, virtual_nodes: int = 150):
        self.ring = {}
        self.sorted_keys = []
        self.nodes = nodes

        for node in nodes:
            for i in range(virtual_nodes):
                key = hashlib.md5(f"{node}:{i}".encode()).hexdigest()
                self.ring[key] = node
                self.sorted_keys.append(key)
        self.sorted_keys.sort()

    def get_preference_list(self, key: str, n: int = 3) -> list:
        if not self.sorted_keys:
            return []
        
        hash_key = hashlib.md5(key.encode()).hexdigest()
        idx = bisect.bisect(self.sorted_keys, hash_key)
        
        pref = []
        for i in range(len(self.sorted_keys)):
            node_id = self.ring[self.sorted_keys[(idx + i) % len(self.sorted_keys)]]
            if node_id not in pref:
                pref.append(node_id)
            if len(pref) >= n:
                break
        return pref