import uvicorn
from server.server import app
from server.connection_manager import ConnectionManager
from server.queues import QueueManager


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    queue_manager = QueueManager()
    connection_manager.set_queue_manager(queue_manager)
    queue_manager.set_message_receiver(connection_manager)

    uvicorn.run(app, host="0.0.0.0", port=5000)
