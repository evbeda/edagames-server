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

    def tearDown(self) -> None:
        del QueueManager.instance

    @patch('pika.BlockingConnection', new=MagicMock())
    def test_get_instance(self):
        del QueueManager.instance
        instance_1 = QueueManager.get_instance()
        instance_2 = QueueManager.get_instance()
        self.assertEqual(instance_1, instance_2)

    def test_listen(self):
        pass

    def test_message_callback(self):
        pass

    def test_send(self):
        pass

    def test_register_client(self):
        pass

    def test_unregister_client(self):
        pass
