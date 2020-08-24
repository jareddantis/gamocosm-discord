import logging
import os
from mcstatus import MinecraftServer
from discord.ext import commands
from discord import Embed


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
        mc_url = os.environ['publicUrl'] if 'publicUrl' in os.environ else domain
        mc_invite = f'! Play at **{mc_url}**' if mc else ''

        # Response
        is_online = server and mc
        emoji = ':gear:' if pending is not None else ':white_check_mark:' if is_online else ':x:'
        server_state = str(pending) if pending is not None else 'up' if is_online else 'down'
        response_title = f"{emoji} Server is {server_state}{mc_invite}"
        response_body = Embed(color=0xffa41c if pending is not None else 0x80ea5b if is_online else 0xff371c)
        response_body.add_field(name="Friendly URL", value=mc_url, inline=True)
        response_body.add_field(name="Minecraft server", value='Up' if mc else 'Down', inline=True)
        response_body.add_field(name="DigitalOcean server", value='Up' if server else 'Down', inline=True)
        response_body.add_field(name="Alternate URL", value=domain, inline=True)
        response_body.add_field(name="Direct IP", value=ip, inline=True)
        if mc:
            # Query MC server
            mc_api = MinecraftServer.lookup(domain)
            mc_status = mc_api.status()
            mc_query = mc_api.query()
            mc_sw_ver = mc_query.software.version
            mc_sw_dist = mc_query.software.brand
            mc_players_count = mc_status.players.online
            mc_players_max = mc_status.players.max
            mc_players = ', '.join(mc_query.players.names)
            response_body.add_field(name="Bot-to-server ping", value=f"{mc_status.latency} ms", inline=True)
            response_body.add_field(name="Server version", value=f"{mc_sw_ver} ({mc_sw_dist})")
            response_body.add_field(name=f"Players online ({mc_players_count}/{mc_players_max})", value=mc_players)
        await ctx.send(response_title)
        await ctx.send(embed=response_body)

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

    @commands.command(aliases=['restart'])
    async def reboot(self, ctx):
        """Reboots the DigitalOcean VPS. Also `/restart`."""
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
        """Stops the Minecraft server"""
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

    @commands.command(aliases=['cmd'])
    async def command(self, ctx, *args):
        """Issues a command to the Minecraft server. Also `/cmd`."""
        if 'allowCommands' in os.environ and os.environ['allowCommands'] == 'true':
            if len(args):
                cmd = ' '.join(args)
                await ctx.send(f"Issuing command `/{cmd}` to server.")
                response = api_error_handler(self.api.command(cmd))
            else:
                response = 'Missing command.'
        else:
            response = 'Server commands were disabled for this bot.'
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command()
    async def backup(self, ctx):
        """Starts remote backup. Requires Minecraft server to be paused."""
        response = api_error_handler(self.api.backup())
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")

    @commands.command(aliases=['dl'])
    async def download(self, ctx):
        """Grabs a ZIP download link for the world. Also `/dl`."""
        response = api_error_handler(self.api.download())
        await ctx.send(response)
        logging.info(f"'{ctx.command}' command called by {ctx.author}. Response was '{response}'")
