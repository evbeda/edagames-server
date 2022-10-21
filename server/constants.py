# Websocket events
EVENT_SEND_CHALLENGE = 'challenge'
EVENT_SEND_ERROR = 'error'
EVENT_SEND_PENALIZE = 'penalize'
EVENT_SEND_YOUR_TURN = 'your_turn'
EVENT_LIST_USERS = 'list_users'
EVENT_GAME_OVER = 'game_over'
EVENT_FEEDBACK = 'feedback'

# Connection manager constants
CLIENT_LIST_KEY = 'clients'

# Exceptions
GAMEIDERROR = 'GAMEID_ERROR'
REDIS_ERROR = -1

# Game constants
DEFAULT_GAME = 'wumpus'
GAME_HOST_PORT = "WUMPUS_HOST_PORT"
GAME_PORT = "localhost:50052"
EMPTY_PLAYER = ''

# Time constants
DEBUG_AWAIT = 60
DEFAULT_EXPIRE = 7200  # default expire of 2hs
NORMAL_AWAIT = 15
TIME_SLEEP = 15
TIME_CHALLENGE = 300
TOKEN_EXPIRE = TIME_SLEEP + 15
LOG_EXPIRE = 21600  # expire time for logs of 6h

# Factory Event
ACCEPT_CHALLENGE = 'accept_challenge'
LIST_USERS = 'list_users'
ASK_CHALLENGE = 'challenge'
ABORT_GAME = 'abort_game'
MOVEMENTS = 'movements'

# search_value / callers
OPPONENT = 'opponent'
CHALLENGE_ID = 'challenge_id'
GAME_ID = 'game_id'
TOURNAMENT_ID = 'tournament_id'
TURN_TOKEN = 'turn_token'
TOKEN_COMPARE = 'token_compare'
LOG = 'log'
PLAIN_SEARCH = 'plain_search'
CLIENT_LIST = 'client'

# dict.get values
DATA = 'data'
DEBUG_MODE = 'debug_mode'
GAME_NAME = 'game'
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

# Log constants
LOG_PAGE_SIZE = 20

# Rabbit constants
RABBIT_CLIENT_EXCHANGE = 'client_messages'
RABBIT_CANCEL_TIMEOUT = 5.0
