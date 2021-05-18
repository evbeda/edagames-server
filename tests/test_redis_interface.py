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
