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

    def __init__(self, client, api):
        self.client = client
        self.api = api
        self.busy = False
        self.current_action = ""


class Diagnostic(Category):
    """Diagnostic information for Bot"""

    def __init__(self, client, api):
        Category.__init__(self, client, api)

    @commands.command()
    async def ping(self, ctx):
        """The latency of the bot"""
        response = f"Pong! {int(self.client.latency * 1000)}ms"
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def status(self, ctx):
        """Current status of the server"""
        raw_response = self.api.status()

        # Query DigitalOcean
        server = raw_response['server']
        pending = raw_response['status']
        domain = raw_response['domain']
        ip = raw_response['ip']
        mc = raw_response['minecraft']
        mc_url = os.environ['publicUrl'] if os.environ['publicUrl'] else domain
        mc_invite = f'! Play at **{mc_url}**' if mc else ''

        # Response
        is_online = server and mc
        emoji = ':gear:' if pending is not None else ':white_check_mark:' if is_online else ':x:'
        server_state = str(pending) if pending is not None else 'up' if is_online else 'down'
        response_title = f"{emoji} Server is {server_state}{mc_invite}"
        response_body = f"```\nMinecraft server: {'' if mc else 'not '}running\n" \
            f"DigitalOcean VPS: {'up' if server else 'down'}\n" \
            f"Pending operations: {pending}\n" \
            f"VPS direct IP: {ip}\n" \
            f"VPS CloudFlare alias: {domain}\n"
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
        await ctx.send(response_title)
        await ctx.send(response_body)

        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was {response_body}")


class DOServer(Category):
    """Control the DO server"""

    def __init__(self, client, api):
        Category.__init__(self, client, api)

    @commands.command()
    async def start(self, ctx):
        """Starts the DigitalOcean VPS"""
        self.busy = False
        await ctx.send('Starting server, please wait. This will take a few minutes.')
        response = api_error_handler(self.api.start())
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def stop(self, ctx):
        """Stops the DigitalOcean VPS"""
        if self.busy:
            await ctx.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await ctx.send('Stopping server, please wait. This will take a few minutes.')
            response = api_error_handler(self.api.stop())
            await ctx.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def reboot(self, ctx):
        """Reboots the DigitalOcean VPS"""
        if self.busy:
            await ctx.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            response = api_error_handler(self.api.reboot())
            await ctx.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")


class Minecraft(Category):
    """Control the Minecraft server"""

    def __init__(self, client, api):
        Category.__init__(self, client, api)

    @commands.command()
    async def pause(self, ctx):
        """Stops the Minecraft Server"""
        if self.busy:
            await ctx.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await ctx.send('Pausing Minecraft server, please wait.')
            response = api_error_handler(self.api.pause())
            await ctx.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def resume(self, ctx):
        """Starts the Minecraft server"""
        if self.busy:
            await ctx.send(f'Server is currently busy with your last command `{self.current_action}`')
        else:
            self.busy = True
            self.current_action = ctx.command
            await ctx.send('Resuming Minecraft server, please wait.')
            response = api_error_handler(self.api.resume())
            await ctx.send(response)
            self.busy = False
            logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def command(self, ctx, *args):
        """Issues a command to the Minecraft server"""
        if len(args):
            cmd = ' '.join(args)
            await ctx.send(f"Issuing command `/{cmd}` to server.")
            response = api_error_handler(self.api.command(cmd))
        else:
            response = 'Missing command.'
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def save(self, ctx):
        """Tells the server to save the current world immediately"""
        await ctx.send('Telling server to save world now. This might take a while depending on world size.')
        response = api_error_handler(self.api.command('save-all'))
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def backup(self, ctx):
        """Remotely backups the world on the server. Requires VPS to be on but Minecraft server to be paused."""
        response = api_error_handler(self.api.backup())
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def download(self, ctx):
        """Grabs a local download link for the world file. Requires VPS to be on but Minecraft server to be paused."""
        response = api_error_handler(self.api.download())
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")
