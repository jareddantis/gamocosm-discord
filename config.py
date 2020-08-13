import os


def get_config():
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
