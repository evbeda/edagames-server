import unittest
from unittest.mock import patch

from server.game import Game
from server.constants import (
    DEFAULT_GAME,
    GAME_STATE_PENDING,
)


class TestGame(unittest.TestCase):

    def test_game(self):
        challenge_id = 'id_test'
        challenger = 'User 1'
        challenged = 'User 2'
        with patch('uuid.uuid4', return_value=challenge_id):
            game = game = Game([challenger, challenged], 393923)
            self.assertEqual([challenger, challenged], game.players)
            self.assertEqual(DEFAULT_GAME, game.name)
            self.assertEqual(challenge_id, game.challenge_id)
            self.assertEqual(None, game.game_id)
            self.assertEqual(None, game.turn_token)
            self.assertEqual(GAME_STATE_PENDING, game.state)

    def test_next_turn(self):
        turn_token = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
        game = Game(['p1', 'p2'], 123)
        with patch('uuid.uuid4', return_value=turn_token):
            game.next_turn()
            self.assertEqual(game.turn_token, turn_token)
