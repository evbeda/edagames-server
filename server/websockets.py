import server.websocket_events as websocket_events
from server.connection_manager import manager
import requests
import server.web_urls as web_urls
import json


async def notify_challenge_to_client(client: str, opponent: str, game_id: str):
    await manager.send(
        client,
        websocket_events.EVENT_SEND_CHALLENGE,
        {
            'opponent': opponent,
            'game_id': game_id,
        },
    )


async def notify_error_to_client(client: str, error: str):
    await manager.send(
        client,
        websocket_events.EVENT_SEND_ERROR,
        {
            'Error': error,
        },
    )


def notify_game_created(challenge_id, game_id):
    requests.post(
        web_urls.GAME_URL,
        json=json.dumps({
            'challenge_id': challenge_id,
            'game_id': game_id,
        })
    )


async def notify_your_turn(client: str, data: dict):
    await manager.send(
        client,
        websocket_events.EVENT_SEND_YOUR_TURN,
        data
    )
