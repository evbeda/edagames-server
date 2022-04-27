from typing import Dict, List


class AuthenticationError(BaseException):
    pass


class ConnectionManager:
    instance: 'ConnectionManager'

    async def connect(self, *args, **kwargs):
        raise NotImplementedError

    async def disconnect(self, client_id: str):
        raise NotImplementedError

    async def notify_user_list_changed(self):
        raise NotImplementedError

    async def broadcast(self, event: str, data: Dict):
        raise NotImplementedError

    async def bulk_send(self, clients: List[str], event: str, data: Dict):
        raise NotImplementedError

    async def send(self, client: str, event: str, data: Dict):
        raise NotImplementedError

    async def _send(self, *args, **kwargs):
        raise NotImplementedError
