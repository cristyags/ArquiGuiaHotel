from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.services import notification_service
from app.services.auth_service import decode_token


router = APIRouter()


@router.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    token = websocket.query_params.get("token", "")
    try:
        token_data = decode_token(token)
        if token_data.user_id is None:
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    notification_service.register_ws(token_data.user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notification_service.unregister_ws(token_data.user_id)
