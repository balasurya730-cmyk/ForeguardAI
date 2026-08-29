"""
Manages active WebSocket connections and broadcasts JSON events to every
connected dashboard client. This is how the frontend gets machine, gas,
safety and alert updates without polling / page refresh.
"""
import asyncio
import json
import logging
from typing import List

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("forgeguard.websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info("WebSocket connected. Total: %d", len(self.active_connections))

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, event_type: str, payload: dict):
        """Send a {type, data} JSON message to every connected client."""
        message = json.dumps({"type": event_type, "data": payload}, default=str)
        stale = []
        async with self._lock:
            connections = list(self.active_connections)
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        if stale:
            async with self._lock:
                for c in stale:
                    if c in self.active_connections:
                        self.active_connections.remove(c)

    async def handle_client(self, websocket: WebSocket):
        """Keep the connection open; the dashboard is read-mostly so we just
        drain any client keepalive/pings and detect disconnects."""
        await self.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except Exception:
            await self.disconnect(websocket)


manager = ConnectionManager()
