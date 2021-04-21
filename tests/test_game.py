import unittest
from server.game import Game


class TestServer(unittest.TestCase):
    def setUp(self):
        self.game = Game('player1', 'player2')
