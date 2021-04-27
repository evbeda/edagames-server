from server.factory_event_server import FactoryServerEvent
import unittest
from parameterized import parameterized
from server.server_event import AcceptChallenge, Movents


class TestFactoryServerEvent(unittest.TestCase):
    @parameterized.expand([
        (
            {'action': 'accept_challenge'}, 'client'
        )
    ])
    def test_factory_server_event(self, data, client):
        event = FactoryServerEvent().get_event(data, client)
        self.assertIsInstance(event, AcceptChallenge)

    @parameterized.expand([
        (
            {'action': 'movents'}, 'client'
        )
    ])
    def test_factory_server_default(self, data, client):
        event = FactoryServerEvent().get_event(data, client)
        self.assertIsInstance(event, Movents)
