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

    def test_next_turn(self):
        game = Game(['p1', 'p2'], 123)
        turn_token = {'turn_token': '0000001'}
        token = game.next_turn()
        self.assertEqual(token, turn_token)
