import asyncio
import websockets
import jwt
from urllib.parse import parse_qs


token_key = 'EDAGame$!2021'
users_connected = set()


async def session(websocket, path, token_key):

    path = path[2:]
    dict_path = parse_qs(path)
    encoded_token = dict_path.get('token')[0].encode()
    user_to_connect = jwt.decode(encoded_token, token_key, algorithms=["HS256"])
    users_connected.add(user_to_connect.get('username'))


if __name__ == '__main__':
    start_server = websockets.serve(session, "localhost", 5000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
