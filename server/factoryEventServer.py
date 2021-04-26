from server.severEvent import AcceptChallenge


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        if data.get('action') == 'accept_challenge':
            return AcceptChallenge(data, client)
