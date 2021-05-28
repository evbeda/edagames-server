from hashlib import sha1
import json
from redis.exceptions import DataError

import unittest
from unittest.mock import MagicMock, patch
from parameterized import parameterized
import fakeredis
import redis

from server.redis import (
    add_to_set,
    append_to_stream,
    delete_key,
    remove_from_set,
    save_string,
    get_string,
    get_stream,
)

from server.constants import (
    LOG_PAGE_SIZE,
    REDIS_ERROR,
)


class TestRedis(unittest.TestCase):

    def setUp(self) -> None:
        self.test_dataset = [
            ('1621518371938-0', {'data': '{"action": "move", "data": {"asd": "000001"}}'}),
            ('1621518373107-0', {'data': '{"action": "move", "data": {"asd": "000002"}}'}),
            ('1621518374244-0', {'data': '{"action": "move", "data": {"asd": "000003"}}'}),
            ('1621518375270-0', {'data': '{"action": "move", "data": {"asd": "000004"}}'}),
            ('1621518375935-0', {'data': '{"action": "move", "data": {"asd": "000005"}}'}),
            ('1621518376462-0', {'data': '{"action": "move", "data": {"asd": "000006"}}'}),
            ('1621518379882-0', {'data': '{"action": "move", "data": {"asd": "000007"}}'}),
            ('1621518380612-0', {'data': '{"action": "move", "data": {"asd": "000008"}}'}),
            ('1621518381212-0', {'data': '{"action": "move", "data": {"asd": "000009"}}'}),
            ('1621518381789-0', {'data': '{"action": "move", "data": {"asd": "000010"}}'}),
            ('1621518382350-0', {'data': '{"action": "move", "data": {"asd": "000011"}}'}),
            ('1621518382902-0', {'data': '{"action": "move", "data": {"asd": "000012"}}'}),
            ('1621518383439-0', {'data': '{"action": "move", "data": {"asd": "000013"}}'}),
            ('1621518383999-0', {'data': '{"action": "move", "data": {"asd": "000014"}}'}),
            ('1621518384576-0', {'data': '{"action": "move", "data": {"asd": "000015"}}'}),
            ('1621518385153-0', {'data': '{"action": "move", "data": {"asd": "000016"}}'}),
            ('1621518385561-0', {'data': '{"action": "move", "data": {"asd": "000017"}}'}),
            ('1621518386946-0', {'data': '{"action": "move", "data": {"asd": "000018"}}'}),
            ('1621518387067-0', {'data': '{"action": "move", "data": {"asd": "000019"}}'}),
            ('1621518388078-0', {'data': '{"action": "move", "data": {"asd": "000020"}}'}),
            ('1621518388234-0', {'data': '{"action": "move", "data": {"asd": "000021"}}'}),
            ('1621518388937-0', {'data': '{"action": "move", "data": {"asd": "000022"}}'}),
            ('1621518389394-0', {'data': '{"action": "move", "data": {"asd": "000023"}}'}),
            ('1621518389658-0', {'data': '{"action": "move", "data": {"asd": "000024"}}'}),
            ('1621518389901-0', {'data': '{"action": "move", "data": {"asd": "000025"}}'}),
            ('1621518390214-0', {'data': '{"action": "move", "data": {"asd": "000026"}}'})
        ]

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

    @parameterized.expand([
        (
            'test_game_0000_0001',
            None,
            0,
            '1621518388234-0',
            True,
        ),
        (
            'test_game_0000_0002',
            '1621518388234-0',
            20,
            '1621518390214-0',
            False,
        ),
    ])
    @patch('server.redis.save_string')
    @patch('server.redis.redis_data')
    def test_get_stream(
        self,
        key,
        next_item,
        next_item_index,
        expected_next_item,
        has_token,
        redis_patched,
        save_string_patched
    ):
        if next_item:
            expected_next_prev_token = sha1(next_item.encode()).hexdigest()
        else:
            next_item = '-'
            expected_next_prev_token = None
        expected_log = dict(self.test_dataset[next_item_index:next_item_index + LOG_PAGE_SIZE]).values()
        redis_patched.xrange.return_value = self.test_dataset[next_item_index:next_item_index + LOG_PAGE_SIZE + 1]
        log, next_token = get_stream(key, next_item)
        redis_patched.xrange.assert_called_with(key, min=next_item, count=LOG_PAGE_SIZE + 1)
        self.assertEqual(list(log), list(expected_log))
        if has_token:
            expected_next_token = sha1(expected_next_item.encode()).hexdigest()
            save_string_patched.assert_called_with(
                next_token,
                json.dumps((expected_next_item, expected_next_prev_token)),
            )
        else:
            expected_next_token = None
        self.assertEqual(next_token, expected_next_token)

    @patch('server.redis.logger')
    @patch('server.redis.redis_data')
    def test_get_stream_redis_error(self, redis_patched, logger_patched):
        redis_patched.xrange.side_effect = redis.RedisError
        get_stream('key')
        logger_patched.error.assert_called()

    @patch("server.redis.redis_data", new_callable=fakeredis.FakeStrictRedis)
    def test_add_to_set(self, redis_patched):
        key = 'test_key'
        value = 'test_value'
        add_to_set(key, value)
        assert redis_patched.sismember(key, value)

    @patch("server.redis.redis_data", new_callable=fakeredis.FakeStrictRedis)
    def test_remove_from_set(self, redis_patched):
        key = 'test_key'
        values = ['test_value1', 'test_value2']
        redis_patched.sadd(key, *values)
        remove_from_set(key, values[0])
        assert not redis_patched.sismember(key, values[0])

    @parameterized.expand([
        (add_to_set, 'sadd', {'key': 'test_key', 'value': 'test_value'}),
        (remove_from_set, 'srem', {'key': 'test_key', 'value': 'test_value'}),
        (delete_key, 'delete', {'key': 'test_key'}),
    ])
    @patch('server.redis.logger')
    @patch("server.redis.redis_data")
    def test_data_error(self, method, patched_method, args, redis_patched, logger_patched):
        getattr(redis_patched, patched_method).side_effect = DataError()
        method(**args)
        logger_patched.error.assert_called()
