import logging
import os
from mcstatus import MinecraftServer
from discord.ext import commands


def api_error_handler(err):
    if not err:
        return "Action successfully triggered."
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
        mc = raw_response['minecraft']
        mc_url = os.environ['publicUrl'] if os.environ['publicUrl'] else domain
        mc_invite = f'Play at **{mc_url}**' if mc else ''

        # Response
        is_online = server and mc
        emoji = ':white_check_mark:' if is_online else ':x:'
        response_title = f"**Server is {'up' if is_online else 'down'}** {emoji} {mc_invite}"
        response_body = f"```\nMinecraft server software: {'' if mc else 'not '}running\n" \
            f"DigitalOcean VPS: {'up' if server else 'down'}\n" \
            f"Pending operations: {pending}\n" \
            f"VPS direct IP: {ip}\n" \
            f"VPS Cloudflare alias: {domain}\n"
        if mc:
            # Query MC server
            mc_api = MinecraftServer.lookup(domain)
            mc_status = mc_api.status()
            mc_query = mc_api.query()
            mc_players = ', '.join(mc_query.players.names)
            response_body += f"Server version: {mc_query.software.version} ({mc_query.software.brand})\n" \
                f"Bot-to-server latency: {mc_status.latency} ms\n" \
                f"Players online ({mc_status.players.online}/{mc_status.players.max}): {mc_players}"
        response_body += '```'
        await channel.send(response_title)
        await channel.send(response_body)

        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was {response_body}")


class DOServer(Category):
    """Control the DO server"""

    def __init__(self, client, discord_channel, api):
        Category.__init__(self, client, discord_channel, api)

    @commands.command()
    async def start(self, ctx):
        """Starts the DigitalOcean VPS"""
        channel = self.client.get_channel(self.discord_channel)
        self.busy = False
        await channel.send('Starting server, please wait. This will take a few minutes.')
        response = api_error_handler(self.api.start())
        await channel.send(response)
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
