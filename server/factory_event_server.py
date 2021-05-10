from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
    Challenge,
)
from server.constants import (
    ACCEPT_CHALLENGE,
    LIST_USERS,
    ASK_CHALLENGE,
)


EVENT = {
    ACCEPT_CHALLENGE: AcceptChallenge,
    LIST_USERS: ListUsers,
    ASK_CHALLENGE: Challenge,
}


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        event = EVENT.get(data.get('action'), Movements)
        return event(data, client)
