import logging
import os
from mcstatus import MinecraftServer
from discord.ext import commands


def api_error_handler(err):
    if not err:
        return "Action succesfully triggered"
    else:
        return err


class Category(commands.Cog):
    """Base class for command category"""

    def __init__(self, client, discord_channel, api):
        self.client = client
        self.discord_channel = discord_channel
        self.api = api
        self.busy = False
        self.current_action = ""


class Diagnostic(Category):
    """Diagnostic information for Bot"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def ping(self, ctx):
        """The latency of the bot"""
        channel = self.client.get_channel(self.discord_channel)
        response = f"Pong! {int(self.client.latency * 1000)}ms"
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def status(self, ctx):
        """Current status of the server"""
        channel = self.client.get_channel(self.discord_channel)
        raw_response = self.api.status()

        # Query DigitalOcean
        server = raw_response['server']
        pending = raw_response['status']
        domain = raw_response['domain']
        ip = raw_response['ip']
        vps_status = f">>> Pending operations: **{pending}**\n" \
            f"Gamocosm alias: `{domain}`\n" \
            f"Server IP address: `{ip}`"
        await channel.send(f"DigitalOcean server is **{server}**\n")
        await channel.send(vps_status)

        # Query MC server
        mc_api = MinecraftServer.lookup(domain)
        minecraft = raw_response['minecraft']
        minecraft_status = mc_api.status()
        minecraft_query = mc_api.query()
        minecraft_players = ', '.join(minecraft_query.players.names)
        minecraft_url = os.environ['publicUrl'] if os.environ['publicUrl'] else domain
        minecraft_response = f">>> Server hostname: `{minecraft_url}`\n" \
            f"Latency: **{minecraft_status.latency} ms**\n" \
            f"Players online ({minecraft_status.players.online} total): **{minecraft_players}**"
        await channel.send(f"Minecraft server is **{minecraft}**\n")
        await channel.send(minecraft_response)

        logging.info(f"'{ctx.command}' command called by {ctx.author}.")


class DOServer(Category):
    """Control the DO server"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def start(self, ctx):
        """Starts the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        if self.busy:
            await channel.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await channel.send('Starting server, please wait. This will take a few minutes.')
            response = api_error_handler(self.api.start())
            await channel.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def stop(self, ctx):
        """Stops the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        if self.busy:
            await channel.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await channel.send('Stopping server, please wait. This will take a few minutes.')
            response = api_error_handler(self.api.stop())
            await channel.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def reboot(self, ctx):
        """Reboots the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        if self.busy:
            await channel.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await channel.send('Rebooting server, please wait. This will take a few minutes.')
            response = api_error_handler(self.api.reboot())
            await channel.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")


class Minecraft(Category):
    """Control the Minecraft server"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def pause(self, ctx):
        """Stops the Minecraft Server"""
        channel = self.client.get_channel(self.discord_channel)
        if self.busy:
            await channel.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await channel.send('Pausing Minecraft server, please wait.')
            response = api_error_handler(self.api.pause())
            await channel.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def resume(self, ctx):
        """Starts the Minecraft server"""
        channel = self.client.get_channel(self.discord_channel)
        if self.busy:
            await channel.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await channel.send('Resuming Minecraft server, please wait.')
            response = api_error_handler(self.api.resume())
            await channel.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def backup(self, ctx):
        """Remotely backups the world on the Server"""
        channel = self.client.get_channel(self.discord_channel)
        response = api_error_handler(self.api.backup())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def download(self, ctx):
        """Grabs a local download link for the world file"""
        channel = self.client.get_channel(self.discord_channel)
        response = api_error_handler(self.api.download())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")
