import unittest
from server.severEvent import AcceptChallenge
from parameterized import parameterized
from server.game import Game
import server.server as server
from unittest.mock import patch, AsyncMock


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = {'Test Client 1'}
        game = Game('player1', 'player2', 123213123)
        game.uuid_game = "c303282d-f2e6-46ca-a04a-35d3d873712d"
        server.games = [game]
        with patch('server.server.notify_game_created'):
            with patch('server.websockets.notify_error_to_client', new_callable=AsyncMock):
                await AcceptChallenge(data, client)
                self.assertEqual(game.state, 'accepted')
