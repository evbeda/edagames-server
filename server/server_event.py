from server.game import games
from server.websockets import notify_error_to_client, notify_game_created
from server.exception import GameIdException


class ServerEvent(object):
    def run(self):
        raise NotImplementedError


class AcceptChallenge(ServerEvent):
    def __init__(self, response, client):
        self.response = response
        self.client = client
        self.nameEvent = 'Challenge accepted'

    async def run(self):
        game_id = self.response.get('data', {}).get('game_id')
        if game_id is None:
            return await notify_error_to_client(
                self.client,
                str(GameIdException),
            )
        for game in games:
            if game.uuid_game == game_id:
                game.state = 'accepted'
                notify_game_created(game.challenge_id, game_id)


class Movements(ServerEvent):
    def __init__(self, response, client):
        self.response = response
        self.client = client
        self.nameEvent = 'movements'

    async def run(self):
        pass
