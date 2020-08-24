import os


def get_config():
    # The keys below are required config keys. The bot will refuse to run without them.
    # Any other configs that are non-essential can be accessed through os.environ[key].
    keys = ['serverId', 'apiKey', 'discordKey', 'discordChannel', 'discordPrefix']
    config = {}

    for key in keys:
        if key in os.environ:
            if key == 'discordChannel':
                # Discord channel must be an integer
                config[key] = int(os.environ[key])
            else:
                config[key] = os.environ[key]
        else:
            raise RuntimeError(f'Missing configuration key {key}. Please check your build vars.')

    return config
