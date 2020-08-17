# gamocosm-discord

This is a Discord bot that allows you to control your [Gamocosm](https://gamocosm.com/) server from a text channel. Refer to the Gamocosm api documentation ([Gamocosm/Gamocosm](https://github.com/Gamocosm/Gamocosm) issue [#98](https://github.com/Gamocosm/Gamocosm/issues/98)).

This bot is designed to be deployed on a cloud platform service like Heroku. Configuration is performed through build/environment variables.

Included is a Python wrapper for the Gamocosm API (`api.py`). You are free to use it for your own projects.

## Contents

* `api.py` Python wrapper for the Gamocosm API
* `app.py` Main [Discord.py](http://discordpy.rtfd.org/en/latest) app
* `commands.py` All registered commands for the bot as Discord.py Cogs
* `config.py` Handles retrieval of configuration from the build environment

## Requirements

* Python 3 (>= 3.6 because of f-strings)
* `pip install -r requirements.txt` to install packages

## Configuration
1. Refer to the [Discord.py Docs](https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro) to create a Bot account and add it to a guild/server
2. Populate your chosen platform's build vars with your own configuration
    * `serverId`: Gamocosm server id
    * `apiKey`: Gamocosm api key (under advanced tab in server settings)
    * `discordKey`: The Discord bot api token from step 1
    * `discordChannel`: The id for the channel the bot should output messages to. Follow [this tutorial](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-server-ID-)
    * `discordPrefix`: The message prefix for the bot
    * `publicUrl` (optional): The default public server URL shown to users. Useful if you have a custom domain or subdomain pointing to your Gamocosm server.
3. Deploy to your chosen service, or if you're testing locally, `python app.py`.
4. Type `<discordPrefix>help` for a list of commands.

## Documentation
Refer to Docstrings and Comments for function documentation. You can add new commands as a class in `commands.py` that inherits from `Category()`.
