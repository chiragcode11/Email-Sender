from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
from app.api.auth import decode_access_token

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Store active connections
active_connections: Dict[int, Set[WebSocket]] = {}


@router.websocket("/campaigns")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time campaign updates."""
    await websocket.accept()
    
    user_id = None
    
    try:
        # Authenticate
        auth_data = await websocket.receive_text()
        data = json.loads(auth_data)
        token = data.get("token")
        
        if not token:
            await websocket.close(code=1008, reason="No token provided")
            return
        
        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        
        # Add to active connections
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(websocket)
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        if user_id and user_id in active_connections:
            active_connections[user_id].discard(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        if user_id and user_id in active_connections:
            active_connections[user_id].discard(websocket)


async def broadcast_campaign_update(user_id: int, campaign_id: int, data: dict):
    """Broadcast campaign update to all connected clients for a user."""
    if user_id in active_connections:
        message = {
            "type": "campaign_update",
            "campaign_id": campaign_id,
            "data": data
        }
        
        disconnected = set()
        for websocket in active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            active_connections[user_id].discard(ws)


async def broadcast_email_event(user_id: int, event_data: dict):
    """Broadcast email event to all connected clients for a user."""
    if user_id in active_connections:
        message = {
            "type": "email_event",
            "data": event_data
        }
        
        disconnected = set()
        for websocket in active_connections[user_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            active_connections[user_id].discard(ws)
