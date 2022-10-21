import unittest
from unittest.mock import patch

from parameterized.parameterized import parameterized

from server.game import data_challenge, identifier, next_turn
from server.constants import DEFAULT_GAME
from tests.test_scenarios import (
    DATA_CHALLENGE_SCENARIO_DEBUG_FALSE,
    DATA_CHALLENGE_SCENARIO_DEBUG_TRUE,
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
            "debug_false",
            ["JuanBot", "PedroBot"],
            ["JuanBot"],
            False,
            DATA_CHALLENGE_SCENARIO_DEBUG_TRUE,
        ),
        (
            "debug_true",
            ["JuanBot", "PedroBot"],
            ["JuanBot"],
            True,
            DATA_CHALLENGE_SCENARIO_DEBUG_FALSE,
        ),
    ])
    def test_data_challenge(
        self,
        name,
        players,
        accepted,
        debug_mode,
        expected,
    ):
        res = data_challenge(players, accepted, DEFAULT_GAME, debug_mode)
        self.assertEqual(res, expected)
