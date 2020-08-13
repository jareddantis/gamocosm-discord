import logging
import sys
import commands as cmds
from discord import Activity, ActivityType
from discord.ext.commands import Bot
from discord.ext.tasks import loop
from api import Server
from config import get_config

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

config = get_config()
server_id = config['serverId']
api_key = config['apiKey']
discord_key = config['discordKey']
discord_channel = int(config['discordChannel'])

server = Server(server_id, api_key)
client = Bot(command_prefix=config['discordPrefix'])


@client.event
async def on_ready():
    logging.info(f'Bot is ready. We have logged in as {client.user}')
    server.last_state = server.online() == 'online'
    server.last_mc_state = server.minecraft() == 'online'
    server.last_op = server.pending()


@loop(seconds=15)
async def update_presence():
    status = server.status()

    # DigitalOcean VPS
    is_online = status['server']
    if server.last_state != is_online:
        # State changed, alert channel
        server.last_state = is_online
        channel = client.get_channel(discord_channel)
        await channel.send(f"DigitalOcean server is now {'up' if is_online else 'down'}.")

    # Current operation
    pending = status['status']
    if server.last_op != pending:
        channel = client.get_channel(discord_channel)
        if pending == 'preparing':
            await channel.send('Firing up Minecraft server, please wait.')
        elif pending == 'rebooting':
            await channel.send('Rebooting server, please wait.')
        elif pending is None and server.last_op == 'saving':
            await channel.send('Server shut down. Thanks for playing!')
        server.last_op = pending

    # Minecraft server
    is_mc_online = status['minecraft']
    if server.last_mc_state != is_mc_online:
        # State changed, alert channel
        server.last_mc_state = is_mc_online
        channel = client.get_channel(discord_channel)
        await channel.send(f"Minecraft server is now {'up. Have fun!' if is_mc_online else 'down.'}")

    # Bot presence
    presence = f"/help | Server {'up' if is_mc_online else 'down'}"
    await client.change_presence(activity=Activity(name=presence, type=ActivityType.listening))


@update_presence.before_loop
async def update_presence_before():
    await client.wait_until_ready()


for category in find_commands(cmds, cmds.Category):
    logging.info(f"Configuring command category {category[1]}")
    client.add_cog(category[1](client, discord_channel, server))

update_presence.start()
client.run(discord_key)
