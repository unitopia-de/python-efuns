from datetime import datetime, timedelta
import ldmud, jwt, os, configparser

config = configparser.ConfigParser()
config['jwt'] = {}
config.read(os.path.expanduser('~/.ldmud-efuns'))
jwtconfig = config['jwt']

JWT_ALGORITHM = jwtconfig.get('algorithm', 'RS256')
JWT_EXP_DELTA_SECONDS = jwtconfig.getint('timeout', 60)
JWT_PRIVATE_KEY_FILE = jwtconfig.get('keyfile', None)

if JWT_PRIVATE_KEY_FILE is None:
    print("JWT Key not specified.")

# https://pyjwt.readthedocs.io/en/latest/usage.html#encoding-decoding-tokens-with-rs256-rsa

def efun_get_jwt(mud: str, file: str) -> str:
    """
    SYNOPSIS
            string get_jwt(string mudname, string filename)

    DESCRIPTION
            Returns a JSON Web Token for accessing mudlib files
            from the web.

            This efun is only allowed to be called from a player
            object.
    """

    player = ldmud.efuns.previous_object()
    loadname = ldmud.efuns.load_name(player)
    
    if loadname == '/obj/player' or loadname == '/obj/newplayer':
        if JWT_PRIVATE_KEY_FILE is None:
            raise RuntimeError("JWT Key not specified.")

        with open(JWT_PRIVATE_KEY_FILE, "rb") as in_file:
            private_pem_data = in_file.read()

        payload = {
            'user_id': player.functions.query_real_name(),
            'mud': mud,
            'file': file,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
        }
        return jwt.encode(payload, private_pem_data, JWT_ALGORITHM).decode('ascii')
    else:
        raise ValueError("Invalid Caller.")
