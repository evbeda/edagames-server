from server.server_event import (
    AcceptChallenge,
    Movements,
    ListUsers,
<<<<<<< HEAD
    Challenge,
=======
    AbortGame
>>>>>>> create eda_game
)
from server.constants import (
    ACCEPT_CHALLENGE,
    LIST_USERS,
<<<<<<< HEAD
    ASK_CHALLENGE,
=======
    ABORT_GAME,
>>>>>>> create eda_game
)


EVENT = {
    ACCEPT_CHALLENGE: AcceptChallenge,
    LIST_USERS: ListUsers,
<<<<<<< HEAD
    ASK_CHALLENGE: Challenge,
=======
    ABORT_GAME: AbortGame,
>>>>>>> create eda_game
}


class FactoryServerEvent(object):
    @staticmethod
    def get_event(data, client):
        event = EVENT.get(data.get('action'), Movements)
        return event(data, client)
