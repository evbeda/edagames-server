import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from parameterized import parameterized

from server.redis_interface import (
    redis_get,
    redis_save,
    key_conversion,
)

from server.constants import (
    CHALLENGE_ID,  # caller
    TURN_TOKEN,
    TOKEN_COMPARE,
    BOARD_ID,
    LOG,
    PREFIX_CHALLENGE,  # prefix
    PREFIX_TURN_TOKEN,
    PREFIX_GAME,
    PREFIX_LOG,
    EMPTY_PLAYER,  # web requests
    REDIS_ERROR,  # error
    TIME_SLEEP,  # timers expire
    TIME_CHALLENGE,
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
