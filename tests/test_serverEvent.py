import unittest
from server.server_event import AcceptChallenge
from parameterized import parameterized
from server.game import Game, games
from unittest.mock import patch, AsyncMock


class TestServerEvent(unittest.IsolatedAsyncioTestCase):
    @parameterized.expand([
        ({"action": "accept_challenge", "data": {"game_id": "c303282d-f2e6-46ca-a04a-35d3d873712d"}},),
    ])
    async def test_accept_challenge(self, data):
        client = 'Test Client 1'
        with patch('server.server_event.notify_game_created'):
            with patch('server.server_event.notify_error_to_client', new_callable=AsyncMock):
                with patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d'):
                    game = Game('player1', 'player2', 123213123)
                    games.append(game)
                    await AcceptChallenge(data, client).run()
                    self.assertEqual(game.state, 'accepted')
