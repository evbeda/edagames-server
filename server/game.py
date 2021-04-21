import uuid


class Game:
    def __init__(self, player, challenged_player):
        self.player = player
        self.challenged_player = challenged_player
        self.uuid_game = uuid.uuid4()
