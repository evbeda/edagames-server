from server.constants import RABBIT_CLIENT_EXCHANGE
import unittest
from unittest.mock import MagicMock, patch

from server.queues import QueueManager


class TestQueueAsync(unittest.IsolatedAsyncioTestCase):

    @patch('pika.BlockingConnection', new=MagicMock())
    def setUp(self) -> None:
        self.manager = QueueManager()

    async def test_consume(self):
        self.manager.channel = MagicMock()
        await self.manager._consume()
        self.manager.channel.start_consuming.assert_called()


class TestQueue(unittest.TestCase):

    @patch('pika.BlockingConnection', new=MagicMock())
    def setUp(self) -> None:
        self.manager = QueueManager()
        self.manager.channel = MagicMock()
        self.manager.receiver = MagicMock()

    def test_set_message_receiver(self):
        recv = MagicMock()
        self.manager.set_message_receiver(recv)
        self.assertEqual(self.manager.receiver, recv)

    @patch.object(QueueManager, '_consume', new=MagicMock())
    @patch('asyncio.create_task')
    def test_listen(self, create_task_patched):
        self.manager.listen()
        self.assertIsNotNone(self.manager.listener)
        self.manager.channel.basic_consume.assert_called_with(
            '',
            self.manager.message_callback,
        )
        create_task_patched.assert_called_with(self.manager._consume())

    def test_listen_active(self):
        self.manager.listener = 1
        self.manager.listen()
        self.manager.channel.basic_consume.assert_not_called()
        self.assertEqual(self.manager.listener, 1)

    @patch('asyncio.wait_for', new=MagicMock())
    def test_stop(self):
        listener = MagicMock()
        self.manager.listener = listener
        self.manager.stop()
        self.assertEqual(self.manager.listener, None)

    @patch('asyncio.create_task', new=MagicMock())
    def test_message_callback(self):
        channel = MagicMock()
        method = MagicMock(
            routing_key='some_client',
            delivery_tag=1,
        )
        body = b'list_users//{"users": ["bot1", "bot2", "bot3"]}'
        self.manager.message_callback(channel, method, None, body)
        self.manager.receiver.send.assert_called_with(
            'some_client',
            'list_users',
            {'users': ['bot1', 'bot2', 'bot3']}
        )
        channel.basic_ack.assert_called_with(1)

    def test_send(self):
        self.manager.send(
            'some_client',
            'list_users',
            {"users": ["bot1", "bot2", "bot3"]}
        )
        self.manager.channel.basic_publish.assert_called_with(
            RABBIT_CLIENT_EXCHANGE,
            'some_client',
            'list_users//{"users": ["bot1", "bot2", "bot3"]}',
        )

    def test_register_client(self):
        self.manager.register_client('some_client')
        self.manager.channel.queue_bind.assert_called_with(
            '',
            RABBIT_CLIENT_EXCHANGE,
            'some_client'
        )

    def test_unregister_client(self):
        self.manager.unregister_client('some_client')
        self.manager.channel.queue_unbind.assert_called_with(
            '',
            RABBIT_CLIENT_EXCHANGE,
            'some_client'
        )
