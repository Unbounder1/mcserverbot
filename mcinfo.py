from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from botscripts import MCBotScripts
from podman import PodmanClient
import asyncio
import sys
import traceback
import podscript
import cloudscript
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("URI")
CLIENT_TOKEN = os.getenv("VIRUSTOTAL_TOKEN")
botowners = os.getenv("BOT_OWNERS").split(",")


class MCInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB("serverDB.json").table(name="_default", cache_size=0)
        self.conf = TinyDB("serverDB.json").table(name="_serverconf", cache_size=0)
        self.backups = TinyDB("serverDB.json").table(name="_volumes", cache_size=0)
        
    @commands.command()
    async def list(self, ctx: Context, type=all):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if type == "all":
            servers = [entry["name"] for entry in self.get(ctx)]
            if len(servers) == 0:
                await ctx.send("No servers")
                return
            status = [entry["status"] for entry in self.get(ctx)]
            for i in range(0, len(servers) - 1):
                servers[i] = servers[i] + ": Status `" + status[i] + "`"
            await ctx.send("\n".join(servers))
        elif type == "running" or "up" or "on":
            servers = [entry["name"] for entry in self.get(ctx)]
            status = [entry["status"] for entry in self.get(ctx)]
            for i in range(0, len(servers)):
                servers[i] = servers[i] + ": Status `" + status[i] + "`"
            if len(servers) == 0:
                await ctx.send("No servers")
                return
            else:
                await ctx.send("\n".join(servers))

    @commands.command()
    async def test(self, ctx: Context, name: str, *, args):
        id: Guild.id = ctx.guild.id
        await ctx.send(
            self.db.search((where("serverId") == id) & (where("name") == name))
        )
        return

    @commands.command()
    async def info(self, ctx: Context, name: str):
        id = ctx.guild.id
        servername = name + "." + str(ctx.guild.id)
        owner = self.db.get((where("serverId") == id) & (where("name") == name))[
            "owner"
        ]
        moderatorlst = []
        for moderators in self.db.get(
            (where("serverId") == id) & (where("name") == name)
        )["moderators"]:
            moderatorlst.append("<@" + str(moderators) + ">")
        podmandict = await podscript.podinfo(servername)
        env = {}
        for variables in podmandict["Env"]:
            templst = variables.split("=")
            env[templst[0]] = templst[1]
        try:
            version = env["VERSION"]
        except:
            version = "Latest"
        try:
            type = env["TYPE"]
        except:
            type = "Vanilla"
        await ctx.send(
            f"""
The server "{name}" is a {type} server on version: {version}

Owner: <@{owner}> 
Moderators: {','.join(moderatorlst)}
*the server was created at {podmandict['Created'][:10]}*
        """
        )

    @commands.command()
    async def max(self, ctx: Context):
        querycheck = Query()
        maxperuser = self.conf.get(querycheck.guildId == ctx.guild.id)["maxperuser"]
        maxworlds = self.conf.get(querycheck.guildId == ctx.guild.id)["maxworlds"]
        maxservers = self.conf.get(querycheck.guildId == ctx.guild.id)["maxservers"]
        await ctx.send(
            f"""The max is **{maxperuser} server(s)** per person and a total of **{maxworlds}** worlds
The server's max is **{maxservers} running minecraft servers** in each discord server: Please be considerate of other people.

You have **{len(self.db.search((querycheck.owner == ctx.author.id) & (querycheck.guildId == ctx.guild.id)))}** server(s)
There are **{len(self.db.search((querycheck.status == 'up') & (querycheck.guildId == ctx.guild.id)))}** servers up currently"""
        )
    
    @commands.command()
    async def ip(self, ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.get(ctx, name):
            await ctx.send("Server with this name does not exist.")
            return
        await ctx.send(
            f'The ip for "{name}" is:\n\n`{await cloudscript.findip(name, ctx.guild.id)}`'
        )

    @commands.command()
    async def status(self, ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.get(ctx, name):
            await ctx.send("Server with this name does not exist.")
            return
        processname = name + "." + str(ctx.guild.id)
        message = await podscript.status(processname)
        await ctx.send(f"The server is currently: `{message}`")
        return




    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing some required arguments")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This is not a command. Check your spelling")
        else:
            print(
                "Ignoring exception in command {}:".format(ctx.command), file=sys.stderr
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    def perms(self, ctx: Context, name: str):
        id: Guild.id = ctx.guild.id
        user = ctx.author.id
        for botowner in botowners:
            if botowner == str(user):
                return True
        if (
            self.db.get((where("serverId") == id) & (where("name") == name))["owner"]
            == user
        ):
            return True
        for moderators in self.db.get(
            (where("serverId") == id) & (where("name") == name)
        )["moderators"]:
            if moderators == user:
                return True
        return False

    def blacklisted(self, user: str):
        bannedlst = os.getenv("BOT_BLACKLISTED").split()
        for banned in bannedlst:
            if user == banned:
                return True
            else:
                return False

    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            return self.db.get((where("serverId") == id) & (where("name") == name))
        else:
            return self.db.search((where("serverId") == id))

    async def startup(self, ctx: Context, processname: str, finalip: str):
        with PodmanClient(base_url=uri) as client:
            message = await ctx.send("Starting the Minecraft server...")
            process = client.containers.get(processname)
            is_starting = is_loading = is_finishing = True
            while is_starting:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode("utf-8").find("[init]") != -1:
                        await message.edit(content="Started the Minecraft Server")
                        is_starting = False
                        break
            while is_loading:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode("utf-8").find("Locating download") != -1:
                        await ctx.send("Preparing world...")
                        is_loading = False
                        break
            message = await ctx.send("Setting up the server")
            while is_finishing:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode("utf-8").find("For help") != -1:
                        is_finishing = False
                        break
                logs = list(process.logs(since=1))
                await message.edit(content=logs[-1].decode("utf-8"))
            await message.edit(content=f"The server is up on {finalip}")
            return
    async def serverstop(ctx: Context, name: str):
        with PodmanClient(base_url=uri) as client:
            try:
                process = client.containers.get(name + "." + str(ctx.guild.id))
                process.stop()
            except:
                pass