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

    def tearDown(self) -> None:
        del QueueManager.instance

    @patch('pika.BlockingConnection', new=MagicMock())
    def test_get_instance(self):
        del QueueManager.instance
        instance_1 = QueueManager.get_instance()
        instance_2 = QueueManager.get_instance()
        self.assertEqual(instance_1, instance_2)

    @patch.object(QueueManager, '_consume', new=MagicMock())
    @patch('asyncio.create_task')
    def test_listen(self, create_task_patched):
        self.manager.listen()
        self.assertIsNotNone(self.manager.listener)
        self.manager.channel.basic_consume.assert_called_with(
            '',
            QueueManager.message_callback,
        )
        create_task_patched.assert_called_with(self.manager._consume())

    def test_listen_active(self):
        self.manager.listener = 1
        self.manager.listen()
        self.manager.channel.basic_consume.assert_not_called()
        self.assertEqual(self.manager.listener, 1)

    @patch('server.queues.manager')
    def test_message_callback(self, manager_patched):
        channel = MagicMock()
        method = MagicMock(
            routing_key='some_client',
            delivery_tag=1,
        )
        body = b'list_users//{"users": ["bot1", "bot2", "bot3"]}'
        QueueManager.message_callback(channel, method, None, body)
        manager_patched.send.assert_called_with(
            'some_client',
            'list_users',
            {'users': ['bot1', 'bot2', 'bot3']}
        )
        channel.basic_ack.assert_called_with(1)

    def test_send(self):
        pass

    def test_register_client(self):
        pass

    def test_unregister_client(self):
        pass
