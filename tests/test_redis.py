import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized
import fakeredis
import redis

from server.redis import (
    append_to_stream,
    save_string,
    get_string,
)

from server.constants import (
    REDIS_ERROR,
)


class TestRedis(unittest.TestCase):

    @parameterized.expand([
        # (value, expire, expected_value, expected_ttl)
        (1, None, '1', -1),
        ('fj93j3', 10, 'fj93j3', 10),
    ])
    def test_save_string_valid(self, value, expire, e_value, e_ttl):
        key = 'asd123'
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()) as mock:
            save_string(key, value, expire)
            self.assertEqual(e_value, mock.get(key).decode())
            self.assertEqual(e_ttl, mock.ttl(key))

    @parameterized.expand([
        # (key, value)
        (['key'], 'key'),  # List as a key
        ({10}, ['value']),  # Dict as a key

    ])
    @patch('server.redis.logger.error')
    def test_save_string_exception(self, key, value, mocked):
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()):
            res = save_string(key, value)
            mocked.assert_called_once()
            self.assertEqual(res, REDIS_ERROR)

    def test_get_string_found(self):
        key = 'test_id'
        value = 'test_value'
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()) as r_mock:
            r_mock.set(key, value)
            res = get_string(key)
            self.assertEqual(value, res.decode())

    def test_get_string_found_parsed(self):
        key = 'test_id'
        value = '{"test_value": 10}'
        expected = {'test_value': 10}
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()) as r_mock:
            r_mock.set(key, value)
            res = get_string(key)
            self.assertEqual(expected, res)

    @patch('server.redis.logger.info')
    def test_get_string_not_found(self, mock_logger):
        key = 'test_id_1'
        value = 'test_value'
        wrong_key = 'test_id_2'
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()) as r_mock:
            r_mock.set(key, value)
            res = get_string(wrong_key)
            self.assertEqual(res, None)
            mock_logger.assert_called_once()

    @patch('server.redis.logger.error')
    def test_get_string_error(self, mock_logger):
        key = 'test_id'
        value = 'test_value'
        error_key = ['test_id']
        with patch("server.redis.redis_data", fakeredis.FakeStrictRedis()) as r_mock:
            r_mock.set(key, value)
            get_string(error_key)
            mock_logger.assert_called_once()

    @patch('server.redis.redis_data')
    def test_append_to_stream(self, redis_patched):
        stream = 'some_stream'
        data = {
            'data': 'some_data',
            'dict_data': {
                'etc': 'more data as dict'
            },
        }
        expected = {
            'data': 'some_data',
            'dict_data': '{"etc": "more data as dict"}'
        }
        append_to_stream(stream, data)
        redis_patched.xadd.assert_called_with(stream, expected)

    @patch('server.redis.logger')
    @patch('server.redis.redis_data')
    def test_append_to_stream_redis_error(self, redis_patched, logger_patched):
        redis_patched.xadd.side_effect = redis.RedisError('test')
        append_to_stream('stream', {'data': 'data'})
        logger_patched.error.assert_called()

    @patch('server.redis.logger')
    def test_append_to_stream_parse_error(self, logger_patched):
        append_to_stream('stream', {'data': {'subkey': MagicMock()}})
        logger_patched.error.assert_called()
