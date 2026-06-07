Hệ thống mô phỏng **IoT Sensor Hub** sử dụng **Dynamo-style Leaderless Replication**, **Sloppy Quorum** và **Hinted Handoff**.

---

## Giới thiệu

Project mô phỏng việc thu thập dữ liệu nhiệt độ từ cảm biến IoT (**Temp_Readings**) trong môi trường phân tán. Hệ thống được thiết kế để đạt **High Availability** — vẫn nhận và lưu dữ liệu ngay cả khi có node bị failure (network partition).

Đây là minh họa thực tế cho các khái niệm quan trọng trong Distributed Systems:

- Consistent Hashing
- Leaderless Replication
- Sloppy Quorum (N=3, W=2, R=2)
- Hinted Handoff
- Vector Clock

---

## Features

- **Leaderless Replication**: Không có node leader
- **Sloppy Quorum**: Vẫn ghi dữ liệu khi có node down
- **Hinted Handoff**: Tự động đồng bộ dữ liệu khi node heal
- **Real-time Sensor Simulation** (Temp_Readings)
- **Failure Simulation** qua API (`/admin/toggle_node/{node_id}`)
- **Persistence**: Dữ liệu lưu dưới dạng JSON
- **API Documentation** với Swagger UI

---

## How to Run

```bash
1. Cài đặt
pip install -r requirements.txt

 2. Chạy Gateway (Coordinator)
Bashpython -m src.gateway.main
# hoặc double-click run_gateway.bat (Windows)

3. Chạy Sensor Simulator (ở terminal khác)
Bashpython -m src.sensor.sensor_client
# hoặc double-click run_sensor.bat

4. Truy cập
Main Page: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs
Cluster Status: http://127.0.0.1:8000/api/status
```
