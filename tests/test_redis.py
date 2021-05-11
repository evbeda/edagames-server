import unittest
from unittest.mock import patch
from parameterized import parameterized
import fakeredis

from server.redis import (
    save_string,
)


class TestRedis(unittest.TestCase):

    @parameterized.expand([
        # (value, expire, expected_value, expected_ttl)
        (1, None, '1', -1),
        ('fj93j3', 10, 'fj93j3', 10),
    ])
    def test_save_string_valid(self, value, expire, e_value, e_ttl):
        key = 'asd123'
        with patch("server.redis.r", fakeredis.FakeStrictRedis()) as mock:
            save_string(key, value, expire)
            self.assertEqual(e_value, mock.get(key).decode())
            self.assertEqual(e_ttl, mock.ttl(key))

    @parameterized.expand([
        # (key, value)
        (['key'], 'key'),  # List as a key
        ('key', ['value']),  # List as a value
        ('key', {'id': 'asd123f3'}),  # Dict as a value
    ])
    @patch('server.redis.logger.error')
    def test_save_string_exception(self, key, value, mocked):
        with patch("server.redis.r", fakeredis.FakeStrictRedis()):
            save_string(key, value)
            mocked.assert_called_once()
