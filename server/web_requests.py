import requests
import json

import server.web_urls as web_urls


def notify_game_created(challenge_id, game_id):
    requests.post(
        web_urls.GAME_URL,
        json=json.dumps({
            'challenge_id': challenge_id,
            'game_id': game_id,
        })
    )
