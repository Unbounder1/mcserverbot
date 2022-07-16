from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from podman import PodmanClient
from botscripts import MCBotScripts
import sys
import traceback
import asyncio
import nest_asyncio
import podscript
import cloudscript
from dotenv import load_dotenv
import os

nest_asyncio.apply()
load_dotenv()

uri = os.getenv("URI")
CLIENT_TOKEN = os.getenv("VIRUSTOTAL_TOKEN")
botowners = os.getenv("BOT_OWNERS").split(",")


class MCModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB("serverDB.json").table(name="_default", cache_size=0)
        self.conf = TinyDB("serverDB.json").table(name="_serverconf", cache_size=0)
        self.backups = TinyDB("serverDB.json").table(name="_volumes", cache_size=0)
        self.defaultenv = {
            "GUI": "false",
            "EULA": "true",
            "INIT_MEMORY": "1G",
            "OVERRIDE_SERVER_PROPERTIES": "true",
            "REPLACE_ENV_IN_PLACE": "false",
            "OVERRIDE_OPS": "false",
            "OVERRIDE_WHITELIST": "false",
            "REMOVE_OLD_DATAPACKS": "true",
            "ENABLE_ROLLING_LOGS": "false",
            # RCON
            "ENABLE_RCON": "true",
            "RCON_PASSWORD": "minecraft",  # Advised to change this
            # autopause stuff
            "MAX_TICK_TIME": "-1",
            "ENABLE_AUTOPAUSE": "true",
            "AUTOPAUSE_TIMEOUT_EST": "3600",
            "AUTOPAUSE_KNOCK_INTERFACE": "tap0",
            # autostop stuff
            "ENABLE_AUTOSTOP": "false",
            "AUTOSTOP_TIMEOUT_EST": "172800",  # 2 days
        }
    @commands.command()
    async def stop(self, ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, name):
            await ctx.send("Server with this name does not exist.")
            return
        message = await ctx.send(f"Stopping the server '{name}'...")
        processname = name + "." + str(ctx.guild.id)
        stopping = await podscript.stop(processname)
        await message.edit(content=stopping)
        self.db.update(
            {"status": "down"},
            (where("serverId") == ctx.guild.id) & (where("name") == name),
        )

    @commands.command()
    async def start(self, ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, name):
            await ctx.send("Server with this name does not exist.")
            return
        processname = name + "." + str(ctx.guild.id)
        starting = await podscript.start(processname)
        await ctx.send(starting)
        finalip = await cloudscript.findip(name, ctx.guild.id)
        try:
            await asyncio.wait_for(self.startup(ctx, processname, finalip), timeout=120)
        except asyncio.TimeoutError:
            pass
        self.db.update(
            {"status": "down"},
            (where("serverId") == ctx.guild.id) & (where("name") == name),
        )

    @commands.command()
    async def addplayer(self, ctx: Context, servername: str, whichlst: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.perms(ctx, servername):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, servername):
            await ctx.send("Server with this name does not exist.")
            return
        name = args.split(",")
        addplayers = await podscript.addplayers(
            whichlst, name, servername + "." + str(ctx.guild.id)
        )
        if addplayers == 1:
            await ctx.send(f"Successfully added {args} to the {whichlst}")
        else:
            await ctx.send(
                "Something went wrong. Check your parameters for spelling errors"
            )

    @commands.command()
    async def removeplayer(self, ctx: Context, servername: str, whichlst: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        if not self.perms(ctx, servername):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, servername):
            await ctx.send("Server with this name does not exist.")
            return
        name = args.split(",")
        removeplayers = await podscript.removeplayers(
            whichlst, name, servername + "." + str(ctx.guild.id)
        )
        if removeplayers == 1:
            await ctx.send(f"Successfully removed {args} from the {whichlst}")
        else:
            await ctx.send(
                "Something went wrong. Check your parameters for spelling errors"
            )

    @commands.command()
    async def addmoderator(self, ctx: Context, name: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        id: Guild.id = ctx.guild.id
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        lst = args.split()
        userlst = []
        for user in lst:
            user = user.replace("<", "")
            user = user.replace(">", "")
            user = user.replace("@", "")
            user = user.replace("!", "")
            userlst.append(str(user))
            await ctx.send(f"Added <@{user}> to list of moderators")
        for user in self.db.search((where("serverId") == id) & (where("name") == name))[
            0
        ]["moderators"]:
            userlst.append(user)

        userlst = list(set(userlst))

        self.db.update(
            {"moderators": userlst}, (where("serverId") == id) & (where("name") == name)
        )

    @commands.command()
    async def removemoderator(self, ctx: Context, name: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send("You were blacklisted by the bot owner")
            return
        id: Guild.id = ctx.guild.id
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        moderatorlist = self.db.search(
            (where("serverId") == id) & (where("name") == name)
        )[0]["moderators"]
        lst = args.split()
        userlst = []
        for user in lst:
            user = user.replace("<", "")
            user = user.replace(">", "")
            user = user.replace("@", "")
            user = user.replace("!", "")
            userlst.append(str(user))
        for user in userlst:
            try:
                userlst.remove(user)
                await ctx.send(f"Removed <@{user}> to list of moderators")
            except:
                await ctx.send(f"<@{user}> is not on the list of moderators")
        self.db.update(
            {"moderators": userlst}, (where("serverId") == id) & (where("name") == name)
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

    def blacklisted(user: str):
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