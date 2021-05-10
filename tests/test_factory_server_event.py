from server.factory_event_server import FactoryServerEvent
import unittest
from parameterized import parameterized
from server.server_event import AcceptChallenge, Movements, AbortGame, ListUsers
from server.constants import ACCEPT_CHALLENGE, LIST_USERS, ABORT_GAME


class TestFactoryServerEvent(unittest.TestCase):
    @parameterized.expand([
        ({'action': 'accept_challenge'}, ),
        ({'action': 'abort_game'}, ),
        ({'action': 'list_users'}, ),
    ])
    def test_factory_server_event(self, data):
        client = 'client'
        EVENT = {
            ACCEPT_CHALLENGE: AcceptChallenge,
            LIST_USERS: ListUsers,
            ABORT_GAME: AbortGame,
        }
        event = FactoryServerEvent().get_event(data, client)
        event_server = EVENT.get(data.get('action'), Movements)
        self.assertIsInstance(event, event_server)
