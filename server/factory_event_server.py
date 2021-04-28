from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
)
from server.websocket_events import (
    ACCEPT_CHALLENGE,
    LIST_USERS,
)


EVENT = {
    ACCEPT_CHALLENGE: AcceptChallenge,
    LIST_USERS: ListUsers,
}


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        event = EVENT.get(data.get('action'), Movements)
        return event(data, client)
