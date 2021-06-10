import asyncio
import json
import pika
from pika.exchange_type import ExchangeType

from server.connection_manager import manager

from server.environment import RABBIT_HOST, RABBIT_PORT
from server.constants import RABBIT_CLIENT_EXCHANGE


class QueueManager:

    def __init__(self):
        QueueManager.instance = self
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(RABBIT_CLIENT_EXCHANGE, ExchangeType.direct)
        self.channel.queue_declare(auto_delete=True)
        self.channel.queue_bind('', RABBIT_CLIENT_EXCHANGE)
        self.listener = None

    @staticmethod
    def get_instance():
        instance = getattr(QueueManager, 'instance', None) or QueueManager()
        return instance

    async def consume(self):
        try:
            self.channel.start_consuming()
        except asyncio.CancelledError:
            self.listener = None

    def listen(self):
        if self.listener is None:
            self.channel.basic_consume('', QueueManager.message_callback)
            self.listener = asyncio.create_task(self.consume())

    def stop(self):
        if self.listener:
            self.listener.cancel()

    @staticmethod
    def message_callback(ch, method, properties, body):
        print(body.decode())
        event, data = body.decode().split('//')
        data = json.loads(data)
        manager.send(method.routing_key, event, data)
        ch.basic_ack(method.delivery_tag)

    def send(self, client, event, data):
        self.channel.basic_publish(
            RABBIT_CLIENT_EXCHANGE,
            client,
            '//'.join((event, json.dumps(data)))
        )

    def register_client(self, client):
        self.channel.queue_bind('', RABBIT_CLIENT_EXCHANGE, client)

    def unregister_client(self, client):
        self.channel.queue_unbind('', RABBIT_CLIENT_EXCHANGE, client)
