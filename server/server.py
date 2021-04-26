import starlette
from fastapi import FastAPI, WebSocket
from server.connection_manager import manager
from .router import router
from server.factory_event_server import FactoryServerEvent
import json

app = FastAPI()
app.include_router(router)


@app.websocket("/ws/")
async def session(websocket: WebSocket, token):
    client = await manager.connect(websocket, token)
    if client is None:
        return
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                data = json.loads(msg)
            except json.decoder.JSONDecodeError:
                data = {}
            await FactoryServerEvent.get_event(data, client).run()
            await manager.broadcast(f'Your msg is {data}')
    except starlette.websockets.WebSocketDisconnect:
        manager.remove_user(client)
        return
