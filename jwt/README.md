# Python Efun for JWT generation

The UNItopia mudlib allows access to mudlib files via the Web server.
To authenticate such requests a JWT token is given (for example within
the GMCP protocol). The `get_jwt` efun generates such a token.

The efun needs configuration in the `.ldmud-efuns` config file in the
home directory with the following contents.
```
[jwt]
keyfile = /Path/To/The/PrivateKey.pem
algorithm = RS256   # This is the default if not given
timeout = 60        # This is the default if not given
```
