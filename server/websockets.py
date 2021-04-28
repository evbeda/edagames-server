import server.websocket_events as websocket_events
from server.connection_manager import manager
from typing import Dict, List


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


async def notify_your_turn(client: str, data: Dict):
    await manager.send(
        client,
        websocket_events.EVENT_SEND_YOUR_TURN,
        data,
    )


async def notify_user_list_to_client(client: str, users: List[str]):
    await manager.send(
        client,
        websocket_events.EVENT_LIST_USERS,
        {
            'users': users,
        },
    )
