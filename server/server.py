import starlette
import jwt
import os
import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import json
from typing import Dict

DJANGO_USERS_URI = 'http://localhost:8000/users'
DJANGO_GAME_URI = 'http://localhost:8000/games'

EVENT_SEND_CHALLENGE = 'challenge'

app = FastAPI()
users_connected = set()


# @app.get("/")
# async def read_root():
#     return {"Hello": "World"}


class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, client):
        await websocket.accept()
        self.connections[client] = websocket

    async def broadcast(self, data: str):
        for user, connection in self.connections.items():
            await connection.send_text(data)

    async def send(self, client: str, event: str, data: Dict[str, str]):
        client_websocket = self.connections.get(client)
        if client_websocket is not None:
            client_websocket.send_text(json.dumps({
                'event': event,
                'data': json.dumps(data)
            }))


async def notify_challenge_to_client(client: str, opponent: str, game_id: str):
    await manager.send(
        client,
        EVENT_SEND_CHALLENGE,
        {
            'opponent': opponent,
            'game_id': game_id,
        },
    )


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
        DJANGO_USERS_URI,
        json=json.dumps({
            'users': list(manager.connections.keys()),
        }),
    )


def notify_game_created(challenge_id, game_id):
    requests.post(
        DJANGO_GAME_URI,
        json=json.dumps({
            'challenge_id': challenge_id,
            'game_id': game_id,
        })
    )


manager = ConnectionManager()


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
    uvicorn.run(app, host="0.0.0.0", port=8000)
