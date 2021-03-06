import unittest
from unittest.mock import patch

from parameterized.parameterized import parameterized

from server.game import data_challenge, identifier, next_turn
from server.constants import (
    DEFAULT_GAME,
)


class TestGame(unittest.TestCase):

    def test_identifier(self):
        turn_token = 'c303282d'
        with patch('uuid.uuid4', return_value=turn_token):
            res = identifier()
            self.assertEqual(res, turn_token)

    @patch('server.game.save_string')
    def test_next_turn(self, mock_save_string):
        game_id = 'test_game_id'
        turn_token = 'test_turn_token'
        with patch('server.game.identifier', return_value=turn_token) as mock_identifier:
            res = next_turn(game_id)
            mock_identifier.assert_called_once_with()
            mock_save_string.assert_called_once_with(
                't_' + game_id,
                turn_token,
            )
            self.assertEqual(turn_token, res)

    @parameterized.expand([
        (
            ['Pedro', 'Pablo'],
            '{"players": ["Pedro", "Pablo"], '
            f'"accepted": ["Pedro"], "game": "{DEFAULT_GAME}"}}'
        ),
        (
            ['Pedro', 'Pablo'],
            f'{{"players": ["Pedro", "Pablo"], "accepted": ["Pedro"], "game": "{DEFAULT_GAME}"}}'
        ),
    ])
    def test_data_challenge(self, players, expected):
        res = data_challenge(players, [players[0]], DEFAULT_GAME)
        self.assertEqual(res, expected)
