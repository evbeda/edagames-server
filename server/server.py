import starlette
from fastapi import FastAPI, WebSocket
from server.connection_manager import manager
from .router import router
<<<<<<< HEAD
from server.game import games
from server.websockets import notify_error_to_client, notify_game_created
from server.exception import GameIdException
import json
=======
from server.factoryEventServer import FactoryServerEvent
>>>>>>> create factory

app = FastAPI()
app.include_router(router)


<<<<<<< HEAD
async def accept_challenge(data, client):
    game_id = data.get('data', {}).get('game_id')
    if game_id is None:
        await notify_error_to_client(
            client,
            str(GameIdException),
        )
    for game in games:
        if game.uuid_game == game_id:
            game.state = 'accepted'
            notify_game_created(game.challenge_id, game_id)
=======
def notify_game_created(challenge_id, game_id):
    requests.post(
        web_urls.GAME_URL,
        json=json.dumps({
            'challenge_id': challenge_id,
            'game_id': game_id,
        })
    )
>>>>>>> create factory


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
