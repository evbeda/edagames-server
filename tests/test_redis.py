import unittest
from unittest.mock import patch
import fakeredis

from server.redis import (
    save_string,
)


class TestRedis(unittest.TestCase):
    def test_save_string(self):
        key = 'asd123'
        value = 1
        with patch("server.redis.r", fakeredis.FakeStrictRedis()) as mock:
            save_string(key, value)
