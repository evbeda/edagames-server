import starlette
import jwt
import os
import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import json
import server.django_urls as django_urls
from server.connection_manager import manager
from .router import router

app = FastAPI()
app.include_router(router)


def add_user(token):
    token_key = os.environ.get('TOKEN_KEY')
    encoded_token = token.encode()
    try:
        user_to_connect = jwt.decode(
            encoded_token,
            token_key,
            algorithms=["HS256"],
        )
    except jwt.exceptions.InvalidTokenError:
        return
    return user_to_connect.get('user')


def remove_user(users_to_disconnect):
    del manager.connections[users_to_disconnect]


def update_users_in_django():
    requests.post(
        django_urls.USERS_URL,
        json=json.dumps({
            'users': list(manager.connections.keys()),
        }),
    )


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
    client = add_user(token)
    if client is None:
        await websocket.close()
        return
    await manager.connect(websocket, client)
    try:
        while True:
            msg = await websocket.receive_text()
            await manager.broadcast(f'Your msg is {msg}')
    except starlette.websockets.WebSocketDisconnect:
        remove_user(client)
        return


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
