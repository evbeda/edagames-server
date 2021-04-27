from server.server_event import AcceptChallenge, Movents
from server.websocket_events import ACCEPT_CHALLENGE, MOVENTS


EVENT = {
    ACCEPT_CHALLENGE: AcceptChallenge,
    MOVENTS: Movents
}


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        event = EVENT.get(data.get('action'), 'movents')
        return event(data, client)
