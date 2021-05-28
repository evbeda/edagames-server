import unittest
from unittest.mock import patch
from parameterized import parameterized

from server.redis_interface import (
    redis_delete,
    redis_get,
    redis_save,
    key_conversion,
)

from server.constants import (
    CHALLENGE_ID,
    CLIENT_LIST,
    TURN_TOKEN,
    TOKEN_COMPARE,
    LOG,
    REDIS_ERROR,  # error
    TIME_SLEEP,  # timers expire
    TIME_CHALLENGE,
    MSG_TURN_TOKEN,
)


class TestRedisInterface(unittest.IsolatedAsyncioTestCase):

    @parameterized.expand([
        (CHALLENGE_ID, 'c_test_key'),
        (TURN_TOKEN, 't_test_key'),
        (TOKEN_COMPARE, 't_test_key'),
        (LOG, 'l_test_key'),
    ])
    def test_key_conversion(self, caller, expected):
        key = 'test_key'
        res = key_conversion(key, caller)
        self.assertEqual(res, expected)

    @parameterized.expand([
        # (caller, expire, call_count_save_string, call_count_append_to_stream,)
        (CHALLENGE_ID, TIME_CHALLENGE, 1, 0),
        (TURN_TOKEN, TIME_SLEEP, 1, 0),
        (LOG, None, 0, 1),
    ])
    @patch('server.redis_interface.append_to_stream')
    @patch('server.redis_interface.save_string')
    def test_redis_save(
        self,
        caller,
        expire,
        cc_save,
        cc_append,
        mock_save,
        mock_append,
    ):
        key = 'default_key'
        value = 'default_value'
        converted_key = 'key_with_prefix'
        with patch('server.redis_interface.key_conversion', return_value=converted_key) as mock_key_conversion:
            redis_save(key, value, caller)
            mock_key_conversion.assert_called_once_with(key, caller)
            if self.assertEqual(mock_save.call_count, cc_save):
                mock_save.assert_called_once_with(converted_key, value, expire)
            if self.assertEqual(mock_append.call_count, cc_append):
                mock_append.assert_called_once_with(converted_key, value, expire)

    async def test_redis_get_finded(self):
        key = 'default_key'
        converted_key = 'key_with_prefix'
        caller = TURN_TOKEN
        return_data = 'data'
        with patch('server.redis_interface.key_conversion', return_value=converted_key) as mock_key_conversion:
            with patch('server.redis_interface.get_string', return_value=return_data) as mock_get_string:
                res = await redis_get(key, caller)
                mock_key_conversion.assert_called_once_with(key, caller)
                mock_get_string.assert_called_once_with(converted_key)
                self.assertEqual(res, return_data)

    @patch('server.redis_interface.notify_feedback')
    async def test_redis_get_not_finded(self, mock_feedback):
        key = 'default_key'
        caller = TURN_TOKEN
        client = 'test_client'
        converted_key = 'key_with_prefix'
        return_data = None
        with patch('server.redis_interface.key_conversion', return_value=converted_key) as mock_key_conversion:
            with patch('server.redis_interface.get_string', return_value=return_data) as mock_get_string:
                res = await redis_get(key, caller, client)
                mock_key_conversion.assert_called_once_with(key, caller)
                mock_get_string.assert_called_once_with(converted_key)
                mock_feedback.assert_awaited_once_with(client, f'{MSG_TURN_TOKEN}{key}')
                self.assertEqual(res, return_data)

    @patch('server.redis_interface.notify_error_to_client')
    async def test_redis_get_error(self, mock_error):
        key = 'default_key'
        caller = TURN_TOKEN
        client = 'test_client'
        converted_key = 'key_with_prefix'
        return_data = REDIS_ERROR
        with patch('server.redis_interface.key_conversion', return_value=converted_key) as mock_key_conversion:
            with patch('server.redis_interface.get_string', return_value=return_data) as mock_get_string:
                res = await redis_get(key, caller, client)
                mock_key_conversion.assert_called_once_with(key, caller)
                mock_get_string.assert_called_once_with(converted_key)
                mock_error.assert_awaited_once_with(client, f'DataError in {caller}, send a str')
                self.assertEqual(res, return_data)

    @patch('server.redis_interface.remove_from_set')
    def test_redis_delete_value(self, remove_patched):
        key = 'test_key'
        caller = CLIENT_LIST
        value = 'client_1'
        redis_delete(key, caller, value)
        remove_patched.assert_called_with(key, value)

    @patch('server.redis_interface.delete_key')
    def test_redis_delete(self, delete_patched):
        key = 'test_key'
        caller = CLIENT_LIST
        redis_delete(key, caller)
        delete_patched.assert_called_with(key)
