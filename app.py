import logging
import os
import sys
import commands as cmds
from discord import Activity, ActivityType
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from api import Server


def find_commands(module, clazz):
    """Searches commands.py to find suitable commands to register"""
    for name in dir(module):
        o = getattr(module, name)
        try:
            if (o != clazz) and issubclass(o, clazz):
                yield name, o
        except TypeError:
            pass


logging.basicConfig(handlers=[logging.FileHandler('app.log'), logging.StreamHandler(sys.stdout)],
                    format='[%(asctime)s %(levelname)s] %(message)s', level=logging.INFO)
logging.info("------ APP STARTED ------")

config = {
    'serverId': os.environ['serverId'],
    'apiKey': os.environ['apiKey'],
    'discordKey': os.environ['discordKey'],
    'discordChannel': os.environ['discordChannel'],
    'discordPrefix': os.environ['discordPrefix'],
}
logging.info(f"Config: {config}")
server_id = config['serverId']
api_key = config['apiKey']
discord_key = config['discordKey']
discord_channel = int(config['discordChannel'])

server = Server(server_id, api_key)
logging.info(f"Starting status is: {server._status()}")

client = Bot(command_prefix=config['discordPrefix'])

@client.event
async def on_ready():
    logging.info(f'Bot is ready. We have logged in as {client.user}')

@loop(seconds=15)
async def update_presence():
    status = server._status()
    minecraft_status = ['up' if status['minecraft'] else 'down'][0]
    presence = f'/help | Server {minecraft_status}'
    await client.change_presence(activity=Activity(name=presence, type=ActivityType.listening))

@update_presence.before_loop
async def update_presence_before():
    await client.wait_until_ready()


for category in find_commands(cmds, cmds.Category):
    logging.info(f"Configuring command category {category[1]}")
    client.add_cog(category[1](client, discord_channel, server))

update_presence.start()
client.run(discord_key)
