import requests
import json

import server.web_urls as web_urls


def notify_game_created(game_id):
    requests.post(
        web_urls.GAME_URL,
        json=json.dumps({
            'game_id': game_id,
        })
    )


def notify_end_game_to_web():
    pass
