from fastapi import FastAPI
from src.gateway.routes import router
import uvicorn
from src.gateway.config import HOST, GATEWAY_PORT

app = FastAPI(
    title="IoT Sensor Hub",
    description="""
# Distributed Database Project

Mô phỏng hệ thống cơ sở dữ liệu phân tán sử dụng:

- Leaderless Replication
- Consistent Hashing
- Vector Clock
- Sloppy Quorum
- Hinted Handoff

## Quorum Configuration

- N = 3
- W = 2
- R = 2

## Author

Distributed Database Course Project
""",
    version="1.0.0",
    contact={
        "name": "IoT Sensor Hub"
    }
)

app.include_router(router, prefix="/api")


@app.get(
    "/",
    tags=["System"]
)
async def root():
    return {
        "success": True,
        "message": "IoT Sensor Hub is running"
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=HOST,
        port=GATEWAY_PORT
    )