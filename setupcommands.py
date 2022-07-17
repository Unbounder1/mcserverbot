import discord
from discord.ext import commands
from discord.ext.commands import Context, has_permissions, CheckFailure
from tinydb import TinyDB, where, Query
from dotenv import load_dotenv
from datetime import datetime
import os

botowners = os.getenv('BOT_OWNERS').split(',')
class setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conf = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)

    @commands.command()
    @has_permissions(administrator=True)
    async def setup(self, ctx: Context, name: str):
        await self.logs(ctx)
        query = Query()
        if len(self.conf.search(query.domainprefix == name)) > 0:
            await ctx.send("Another server already has this name. Please choose another")
            return
        if not name.isalnum():
                namesub = name.replace("-", "")
                if not namesub.isalnum():
                    await ctx.send("Only valid characters include letters, numbers, and `-`")
                    return 
        try: maxservers=self.conf.get(query.guildId == ctx.guild.id)['maxservers']
        except: maxservers = 0
        try: maxperuser=self.conf.get(query.guildId  == ctx.guild.id)['maxperuser']
        except: maxperuser = 0
        try: maxworlds=self.conf.get(query.guildId  == ctx.guild.id)['maxworlds']
        except: maxworlds = 0
        self.conf.upsert({'guildId': ctx.guild.id, 'domainprefix': name,'maxservers': maxservers, 'maxperuser': maxperuser, 'maxworlds': maxworlds}, query.guildId == ctx.guild.id)
        await ctx.send(f"Changed this server's prefix to {name}")
    @commands.command()
    async def maxservers(self, ctx: Context, maxservers = 0):
        await self.logs(ctx)
        query = Query()
        if str(ctx.author.id) not in botowners:
            await ctx.send("Only the bot owners can do this.")
            return
        self.conf.update({'maxservers': maxservers}, query.guildId == ctx.guild.id)
        await ctx.send(f"Changed this server's max server count to {maxservers}")
    @commands.command()
    async def maxperuser(self, ctx: Context, maxperuser = 0):
        await self.logs(ctx)
        query = Query()
        if str(ctx.author.id) not in botowners:
            await ctx.send("Only the bot owners can do this.")
            return
        self.conf.update({'maxperuser': maxperuser}, query.guildId == ctx.guild.id)
        await ctx.send(f"Changed this server's max servers per user to {maxperuser}")
    @commands.command()
    async def maxworlds(self, ctx: Context, maxworlds = 0):
        await self.logs(ctx)
        query = Query()
        if str(ctx.author.id) not in botowners:
            await ctx.send("Only the bot owners can do this.")
            return
        self.conf.update({'maxworlds': maxworlds}, query.guildId == ctx.guild.id)
        await ctx.send(f"Changed this server's max worlds per user to {maxworlds}")
    @commands.command()
    async def whatserversamiin(self, ctx: Context):
        activeservers = self.bot.guilds
        print (activeservers)
    # @setup.error
    # async def setuperror(self, ctx: Context, error):
    #     if isinstance(error, CheckFailure):
    #         await ctx.send("Must have administrator permissions to change this")
    async def logs(self, ctx: Context):
        with open('logs.txt', 'a') as logs:
            logs.write(f'\n{datetime.now()}: {ctx.author} in {ctx.guild} has attempted to use the command "{ctx.message.content}"') 
            print (f'\n{datetime.now()}: {ctx.author} in {ctx.guild} has attempted to use the command "{ctx.message.content}"') 
