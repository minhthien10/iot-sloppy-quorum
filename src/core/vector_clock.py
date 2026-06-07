from collections import defaultdict
import copy

class VectorClock:
    def __init__(self):
        self.clock = defaultdict(int)

    def increment(self, node_id: str):
        self.clock[node_id] += 1

    def update(self, other: 'VectorClock'):
        for nid, ts in other.clock.items():
            self.clock[nid] = max(self.clock[nid], ts)

    def dominates(self, other: 'VectorClock') -> bool:
        """self > other"""
        return all(self.clock[n] >= other.clock.get(n, 0) for n in self.clock) and \
               any(self.clock[n] > other.clock.get(n, 0) for n in self.clock)

    def __gt__(self, other):
        return self.dominates(other)

    def to_dict(self):
        return dict(self.clock)

    @classmethod
    def from_dict(cls, data: dict):
        vc = cls()
        vc.clock = defaultdict(int, data or {})
        return vc

    def __str__(self):
        return str(dict(self.clock))