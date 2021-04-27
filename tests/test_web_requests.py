import unittest
import json
from unittest.mock import patch

from server.web_requests import notify_game_created

import server.web_urls as web_urls


class TestWebRequests(unittest.TestCase):

    @patch('requests.post')
    def test_notify_game_created(self, post_patched):
        notify_game_created(
            '00000000-0000-0000-0000-000000000001',
            '123e4567-e89b-12d3-a456-426614174000',
        )

        post_patched.assert_called_with(
            web_urls.GAME_URL,
            json=json.dumps({
                'challenge_id': '00000000-0000-0000-0000-000000000001',
                'game_id': '123e4567-e89b-12d3-a456-426614174000',
            })
        )
