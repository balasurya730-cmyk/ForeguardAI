import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, engine, SessionLocal
import app.models  # noqa: F401  (ensures all models are registered on Base)
from app.websocket.manager import manager
from app.services.runtime_service import runtime_monitor_loop
from app.services.demo_simulator import demo_simulator_loop
from app.services.mqtt_service import start_mqtt_client
from app.services.pruner_service import auto_pruner_loop

from app.routes import auth, machines, runtime, workers, safety, gas, alerts, reports, dashboard, export

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("forgeguard.main")

app = FastAPI(title="ForgeGuard AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve captured evidence images/videos
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(machines.router)
app.include_router(runtime.router)
app.include_router(workers.router)
app.include_router(safety.router)
app.include_router(gas.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(export.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "mode": settings.SYSTEM_MODE}


@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.handle_client(websocket)


# Single-server SPA support: Serve built React frontend from frontend/dist
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if (FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="static_assets")

if FRONTEND_DIST_DIR.exists():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
            from fastapi.exceptions import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        index_path = FRONTEND_DIST_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"detail": "Frontend index.html not found"}


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)

    loop = asyncio.get_event_loop()

    # Background: auto-stop machines whose configured runtime elapsed.
    asyncio.create_task(runtime_monitor_loop(SessionLocal))
    
    # Background: auto-prune old storage data
    asyncio.create_task(auto_pruner_loop(SessionLocal))

    if settings.SYSTEM_MODE == "DEMO":
        logger.info("Starting in DEMO mode: built-in sensor/AI simulator active, no hardware required.")
        asyncio.create_task(demo_simulator_loop())
    else:
        logger.info("Starting in LIVE mode: expecting real ESP32 (MQTT) and camera (AI pipeline) sources.")
        start_mqtt_client(loop)

