import uuid

games = []


class Game:
    def __init__(self, player, challenged_player):
        self.player = player
        self.challenged_player = challenged_player
        self.uuid_game = str(uuid.uuid4())
        self.state = 'pending'
