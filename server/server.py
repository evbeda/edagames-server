import starlette
import jwt
import os
import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import json

DJANGO_USERS_URI = 'http://localhost:8000/users'
DJANGO_GAME_URI = 'http://localhost:8000/games'

app = FastAPI()
users_connected = set()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


class ConnectionManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections['User'] = websocket

    async def broadcast(self, data: str):
        for user, connection in self.connections.items():
            await connection.send_text(data)


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
    users_connected.add(user_to_connect.get('user'))
    return user_to_connect.get('user')


def remove_user(users_to_disconnect):
    users_connected.remove(users_to_disconnect)


def update_users_in_django():
    requests.post(
        DJANGO_USERS_URI,
        json=json.dumps({
            'users': list(users_connected),
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


def true_func():
    return True


manager = ConnectionManager()


@app.websocket("/ws/")
async def session(websocket: WebSocket, token):
    client = add_user(token)
    if client is None:
        await websocket.close()
    await manager.connect(websocket)
    try:
        while true_func():
            msg = await websocket.receive_text()
            print(f"Received {msg}")
            await manager.broadcast(f'Your msg is {msg}')
    except starlette.websockets.WebSocketDisconnect:
        remove_user(client)
        print(f"User {client} disconnected")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
