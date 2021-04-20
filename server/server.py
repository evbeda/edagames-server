import starlette
import jwt
from urllib.parse import parse_qs
import os
import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import json

DJANGO_USERS_URI = 'http://localhost:8000/users'

users_connected = set()
app = FastAPI()


def add_user(path):
    token_key = os.environ.get('TOKEN_KEY')
    try:
        path = path[2:]
    except IndexError:
        return
    dict_path = parse_qs(path)
    encoded_token = dict_path.get('token')[0].encode()
    try:
        user_to_connect = jwt.decode(encoded_token, token_key, algorithms=["HS256"])
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
            'users': list(users_connected.keys()),
        }),
    )


def true_func():
    return True


@app.websocket("/ws")
async def session(websocket: WebSocket):
    client = add_user('')
    if client is None:
        await websocket.close()
    await websocket.accept()
    try:
        while true_func():
            msg = await websocket.receive_text()
            print(f"Received {msg}")
            await websocket.send_text(f'Your msg is {msg}')
    except starlette.websockets.WebSocketDisconnect:
        remove_user(client)
        print(f"User {client} disconnected")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
