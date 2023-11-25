import uvicorn
import os
from server.server import app
from server.websocket_connection_manager import ConnectionManagerWS
from server.apigw_connection_manager import APIGatewayConnectionManager
# from server.queues import QueueManager

connection_managers = {
    'websocket': ConnectionManagerWS,
    'api_gateway': APIGatewayConnectionManager,
}

if __name__ == '__main__':
    connection_manager_class = connection_managers[
        os.getenv('SERVER_CLIENT_CONNECTION_TYPE', 'websocket')]
    connection_manager = connection_manager_class()
    # queue_manager = QueueManager()
    # connection_manager.set_queue_manager(queue_manager)
    # queue_manager.set_message_receiver(connection_manager)

    uvicorn.run('server.server:app', host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), reload=True, workers=2)
