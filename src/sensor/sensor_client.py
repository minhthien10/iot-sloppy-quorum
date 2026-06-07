import requests
import time
import random
from datetime import datetime

class SensorClient:
    def __init__(self, gateway_url: str = "http://127.0.0.1:8000"):
        self.gateway_url = gateway_url

    def send_temp_reading(self):
        """Gửi dữ liệu theo schema Temp_Readings"""
        sensor_id = f"SENSOR_{random.randint(1, 30):02d}"
        temperature = round(random.uniform(18.0, 45.0), 2)
        
        payload = {
            "sensor_id": sensor_id,
            "value": {
                "temperature": temperature,
                "unit": "°C",
                "timestamp": datetime.now().isoformat(),
                "location": random.choice(["Room_A", "Room_B", "Outdoor", "Warehouse"]),
                "status": random.choice(["normal", "warning", "critical"])
            }
        }

        try:
            response = requests.post(f"{self.gateway_url}/api/write", json=payload, timeout=5)
            result = response.json()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📡 {sensor_id} | {temperature}°C → {result.get('status')} "
                  f"(replicas: {result.get('replicas')})")
        except Exception as e:
            print(f"Error: {e}")

    def run(self, seconds: int = 30):
        print(f"Starting Temp_Readings simulation ({seconds} seconds)...")
        end = time.time() + seconds
        count = 0
        while time.time() < end:
            self.send_temp_reading()
            count += 1
            time.sleep(0.05)  
        print(f"Hoàn thành {count} Temp_Readings")


if __name__ == "__main__":
    client = SensorClient()
    client.run(20)