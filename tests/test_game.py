import unittest
from parameterized import parameterized
from unittest.mock import patch

from server.game import Game


class TestGame(unittest.TestCase):
    @parameterized.expand([
        (
            'User 1',
            'User 2',
            393923,
        )
    ])
    def test_game(self, user, challenged_player, challenge_id):
        game = Game([user, challenged_player], challenge_id)
        self.assertIn(user, game.players)
        self.assertIn(challenged_player, game.players)

    @parameterized.expand([
        (
            'c303282d-f2e6-46ca-a04a-35d3d873712d',
        )
    ])
    def test_next_turn(self, turn_token):
        game = Game(['p1', 'p2'], 123)
        with patch('uuid.uuid4', return_value='c303282d-f2e6-46ca-a04a-35d3d873712d'):
            game.next_turn()
            self.assertEqual(game.turn_token, turn_token)
