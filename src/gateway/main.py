from fastapi import FastAPI
from src.gateway.routes import router
import uvicorn
from src.gateway.config import HOST, GATEWAY_PORT

app = FastAPI(title="IoT Sensor Hub - Leaderless Replication")

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "IoT Sensor Hub with Sloppy Quorum is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=GATEWAY_PORT)