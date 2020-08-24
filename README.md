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

* Python 3.6+ (f-string support required)
* `pip install -r requirements.txt` to install packages if testing locally

## Configuration & deployment
1. Refer to the [Discord.py Docs](https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro) to create a Bot account and add it to a guild/server
2. Populate your chosen platform's build vars with your own configuration

|Config key|Description|
|-----|-----|
|`serverId`|Gamocosm server ID|
|`apiKey`|Gamocosm API key (under advanced tab in server settings)|
|`discordKey`|The Discord bot API token from step 1|
|`discordChannel`|The ID for the channel the bot should reply to and receive from. Follow [this tutorial.](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-server-ID-)|
|`discordPrefix`|The message prefix for the bot|
|`publicUrl`|(Optional) The default public server URL shown to users. Useful if you have a custom domain or subdomain pointing to your Gamocosm server.|
|`allowCommands`|(Optional) Set to `true` to make the bot relay commands to the Minecraft server. See [**Minecraft server commands.**](#Minecraft-server-commands)|

3. Deploy to your chosen service, or if you're testing locally, `python app.py`. Note that if you're testing locally, your config must be set as environment variables.
4. Type `<discordPrefix>help` for a list of commands.

## Minecraft server commands
The bot has the optional ability to relay server commands, such as `/teleport` and `/give`, to your Minecraft server.
Just make sure `allowCommands` is set to `true` in your build vars. Any other value will cause this ability to be disabled.

To send commands to your Minecraft server, say `/command <command without leading slash>` or `/cmd <command without leading slash>`.
For instance, to give all players a stack of emeralds, say `/cmd give @a minecraft:emerald 64`.

## Documentation
Refer to Docstrings and Comments for function documentation. You can add new commands as a class in `commands.py` that inherits from `Category()`.
