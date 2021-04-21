import server.websocket_events as websocket_events
from server.connection_manager import manager


async def notify_challenge_to_client(client: str, opponent: str, game_id: str):
    await manager.send(
        client,
        websocket_events.EVENT_SEND_CHALLENGE,
        {
            'opponent': opponent,
            'game_id': game_id,
        },
    )
