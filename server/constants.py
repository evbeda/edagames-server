# Websocket events
EVENT_SEND_CHALLENGE = 'challenge'
EVENT_SEND_ERROR = 'error'
EVENT_SEND_PENALIZE = 'penalize'
EVENT_SEND_YOUR_TURN = 'your_turn'
EVENT_LIST_USERS = 'list_users'
EVENT_GAME_OVER = 'game_over'
EVENT_FEEDBACK = 'feedback'

# Exceptions
GAMEIDERROR = 'GAMEID_ERROR'
REDIS_ERROR = -1

# Game constants
DEFAULT_GAME = 'quoridor'
EMPTY_PLAYER = ''

# Time constants
TIME_SLEEP = 5
TIME_CHALLENGE = 300

# Factory Event
ACCEPT_CHALLENGE = 'accept_challenge'
LIST_USERS = 'list_users'
ASK_CHALLENGE = 'challenge'
ABORT_GAME = 'abort_game'
MOVEMENTS = 'movements'

# search_value / callers
OPPONENT = 'opponent'
CHALLENGE_ID = 'challenge_id'
TURN_TOKEN = 'turn_token'
GAME_ID = 'game_id'
TOKEN_COMPARE = 'token_compare'
GAME_ID = 'game_id'
LOG = 'log'

# dict.get values
DATA = 'data'
GAME_NAME = 'name'
PLAYERS = 'players'

# Prefixes
PREFIX_CHALLENGE = 'c_'
PREFIX_TURN_TOKEN = 't_'
PREFIX_GAME = 'g_'
PREFIX_LOG = 'l_'

# Feedback msgs
MSG_CHALLENGE = 'Not a challenge was found with the following id: '
MSG_TURN_TOKEN = 'Invalid turn token: '
MSG_TOKEN_COMPARE = 'Time limit: '
MSG_GAME_ID = 'Invalid game id: '
