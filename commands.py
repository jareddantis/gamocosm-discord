import logging
import os
from mcstatus import MinecraftServer
from discord.ext import commands


def apiErrorHandler(err):
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
        raw_response = self.api._status()
        pserver = ['online' if raw_response['server'] else 'offline'][0]
        minecraft = ['online' if raw_response['minecraft'] else 'offline'][0]
        pending = raw_response['status']
        domain = raw_response['domain']
        ip = raw_response['ip']

        # Query MC server
        mc_api = MinecraftServer.lookup(domain)
        minecraft_status = mc_api.status()
        minecraft_query = mc_api.query()
        minecraft_players = ', '.join(minecraft_query.players.names)
        minecraft_publicurl = os.environ['publicUrl'] if os.environ['publicUrl'] else domain
        response = f"DigitalOcean server is **{pserver}**\n" \
            f"Pending operations: **{pending}**\n" \
            f"Server hostname: `{minecraft_publicurl}`\n" \
            f"Server IP address: `{ip}`\n\n" \
            "Minecraft server status:\n\n" \
            f">>>State: **{minecraft}**\n" \
            f"Latency: **{minecraft_status.latency} ms**\n" \
            f"Players ({minecraft_status.players.online} total): **{minecraft_players}**"

        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")


class DOServer(Category):
    """Control the DO server"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def start(self, ctx):
        """Starts the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.start())
        await channel.send('Starting server, please wait.')
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def stop(self, ctx):
        """Stops the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.stop())
        await channel.send('Stopping server, please wait.')
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def reboot(self, ctx):
        """Reboots the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.reboot())
        await channel.send('Rebooting server, please wait.')
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")


class Minecraft(Category):
    """Control the Minecraft server"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def pause(self, ctx):
        """Stops the Minecraft Server"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.pause())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def resume(self, ctx):
        """Starts the Minecraft server"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.resume())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def backup(self, ctx):
        """Remotely backups the world on the Server"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.backup())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def download(self, ctx):
        """Grabs a local download link for the world file"""
        channel = self.client.get_channel(self.discord_channel)
        response = apiErrorHandler(self.api.download())
        await channel.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")
