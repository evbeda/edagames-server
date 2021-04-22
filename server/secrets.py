import os


def load_env_var(name: str, default: str = None):
    var = os.environ.get(name, default)
    if var is None:
        raise EnvironmentError
    else:
        return var


JWT_TOKEN_KEY = load_env_var('TOKEN_KEY')
