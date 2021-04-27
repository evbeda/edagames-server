import unittest
from server.game import Game
from parameterized import parameterized


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
