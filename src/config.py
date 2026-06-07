import os
from dotenv import load_dotenv

load_dotenv()

# Replication settings
N = int(os.getenv("N", 3))          # Replication factor
W = int(os.getenv("W", 2))          # Write quorum
R = int(os.getenv("R", 2))          # Read quorum

NODE_IDS = ["node1", "node2", "node3", "node4", "node5"]

DATA_DIR = "data"
HOST = os.getenv("HOST", "127.0.0.1")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", 8000))