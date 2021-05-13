import unittest
from unittest.mock import patch
import fakeredis


from server.game import Game, data_challenge, identifier, next_turn
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
            game = game = Game([challenger, challenged])
            self.assertEqual([challenger, challenged], game.players)
            self.assertEqual(DEFAULT_GAME, game.name)
            self.assertEqual(challenge_id, game.challenge_id)
            self.assertEqual(None, game.game_id)
            self.assertEqual(GAME_STATE_PENDING, game.state)

    def test_next_turn(self):
        with patch("server.redis.r", fakeredis.FakeStrictRedis()) as mock:
            turn_token = 'c303282d-f2e6-46ca-a04a-35d3d873712d'
            game_id = 'c303282d'
            with patch('uuid.uuid4', return_value=turn_token):
                turn_token_new = next_turn(game_id)
                self.assertEqual(turn_token_new, turn_token)
                self.assertEqual(turn_token, mock.get('t_' + game_id).decode())

    def test_to_JSON(self):
        expected = (
            '{"challenge_id": "c303282d", ' +
            '"game_id": null, ' +
            '"name": "quoridor", ' +
            '"players": ["player_1", "player_2"], ' +
            '"state": 0, ' +
            '"timer": null}'
        )
        turn_token = 'c303282d'
        with patch('uuid.uuid4', return_value=turn_token):
            game = Game(['player_1', 'player_2'])
            res = game.to_JSON()
            self.assertEqual(res, expected)

    def test_identifier(self):
        turn_token = 'c303282d'
        with patch('uuid.uuid4', return_value=turn_token):
            res = identifier()
            self.assertEqual(res, turn_token)

    def test_data_challenge(self):
        players = ['Pedro', 'Pablo']
        expected = f'''{{"players": ["Pedro", "Pablo"], "game": "{DEFAULT_GAME}"}}'''
        res = data_challenge(players)
        self.assertEqual(res, expected)
