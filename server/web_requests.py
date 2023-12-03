import requests

import server.web_urls as web_urls


async def notify_end_game_to_web(game_id, tournament_id, data):
    requests.post(
        web_urls.WEB_SERVER_FULL_URL,
        json=({
            'game_id': game_id,
            'tournament_id': tournament_id,
            'data': data,
        })
    )


async def create_game_to_game(players):
    response = requests.post(
        f"{web_urls.GAME_FULL_URL}/games",
        json=({
            'players': players,
        })
    )
    return response.json()

async def execute_action_to_game(game_id, game_data):
    response = requests.post(
        f"{web_urls.GAME_FULL_URL}/games/{game_id}/actions",
        json=({
            'game_data': game_data,
        })
    )
    return response.json()

async def penalize_to_game(game_id):
    response = requests.post(
        f"{web_urls.GAME_FULL_URL}/games/{game_id}/penalizes",
    )
    return response.json()

async def abort_to_game(game_id):
    response = requests.post(
        f"{web_urls.GAME_FULL_URL}/games/{game_id}/abort",
    )
    return response.json()

