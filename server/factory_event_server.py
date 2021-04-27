from server.server_event import AcceptChallenge, Movements
from server.websocket_events import ACCEPT_CHALLENGE


EVENT = {
    ACCEPT_CHALLENGE: AcceptChallenge,
}


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        event = EVENT.get(data.get('action'), Movements)
        return event(data, client)
