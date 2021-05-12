import unittest
from unittest.mock import patch
from parameterized import parameterized
import fakeredis

from server.redis import (
    save_string,
    get_string,
)


class TestRedis(unittest.IsolatedAsyncioTestCase):

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

    @patch('server.redis.notify_feedback')
    async def test_get_string_finded(self, mock_notify_feedback):
        key = 'test_id'
        value = 'test_value'
        client = 'test_client'
        default_caller = 'default_id'
        with patch("server.redis.r", fakeredis.FakeStrictRedis()) as r_mock:
            r_mock.set(key, value)
            # first call gets and deletes the key
            call_1 = await get_string(key, client, default_caller)
            self.assertEqual(value, call_1.decode())
            # second call doesnt find the key
            call_2 = await get_string(key, client, default_caller)
            self.assertEqual(None, call_2)
            mock_notify_feedback.assert_called_once_with(
                client,
                f'{default_caller} not found',
            )
