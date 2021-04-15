import asyncio
import websockets
import jwt
from urllib.parse import parse_qs
import os


users_connected = set()


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


def true_func():
    return True


async def session(websocket, path):
    client = add_user(path)
    if client is None:
        await websocket.close()
    print(f"User {client} connected")
    try:
        while true_func():
            msg = await websocket.recv()
            print(f"Received {msg}")
            await websocket.send(f'Your msg is {msg}')
    except websockets.exceptions.WebSocketException:
        remove_user(client)
        print(f"User {client} disconnected")


if __name__ == '__main__':
    start_server = websockets.serve(session, "localhost", 5000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
