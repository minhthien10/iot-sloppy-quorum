import requests
import time
import random
from datetime import datetime


class SensorClient:
    def __init__(self, gateway_url="http://127.0.0.1:8000"):
        self.gateway_url = gateway_url

    def send_temp_reading(self):
        sensor_id = f"SENSOR_{random.randint(1, 30):02d}"
        temperature = round(random.uniform(18.0, 45.0), 2)

        payload = {
            "sensor_id": sensor_id,
            "value": {
                "temperature": temperature,
                "unit": "°C",
                "timestamp": datetime.now().isoformat(),
                "location": random.choice(
                    ["Room_A", "Room_B", "Outdoor", "Warehouse"]
                ),
                "status": random.choice(
                    ["normal", "warning", "critical"]
                )
            }
        }

        try:
            response = requests.post(
                f"{self.gateway_url}/api/write",
                json=payload,
                timeout=5
            )

            result = response.json()

            # API response mới
            data = result.get("data", {})

            status = result.get("message", "OK")
            replicas = data.get("replicas", 0)

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"📡 {sensor_id} | "
                f"{temperature}°C | "
                f"Replicas={replicas}"
            )

        except Exception as e:
            print(f" Error: {e}")

    def run(self):
        print("=" * 60)
        print(" IoT Sensor Simulator Started ")
        print(" Press Ctrl + C to stop")
        print("=" * 60)

        count = 0

        try:
            while True:
                self.send_temp_reading()
                count += 1

                if count % 20 == 0:
                    print(f"\n✅ Sent {count} sensor readings\n")

                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n")
            print("=" * 60)
            print(f"Simulator stopped")
            print(f" Total readings sent: {count}")
            print("=" * 60)


if __name__ == "__main__":
    client = SensorClient()
    client.run()