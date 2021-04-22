import starlette
import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import json
import server.django_urls as django_urls
from server.connection_manager import manager
from .router import router

app = FastAPI()
app.include_router(router)


def notify_game_created(challenge_id, game_id):
    requests.post(
        django_urls.GAME_URL,
        json=json.dumps({
            'challenge_id': challenge_id,
            'game_id': game_id,
        })
    )


@app.websocket("/ws/")
async def session(websocket: WebSocket, token):
    client = await manager.connect(websocket, token)
    if client is None:
        return
    try:
        while True:
            msg = await websocket.receive_text()
            await manager.broadcast(f'Your msg is {msg}')
    except starlette.websockets.WebSocketDisconnect:
        manager.remove_user(client)
        return


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
