import discord
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, where

class setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('domainnameDB.json').table(name='_default', cache_size = 0)

    @commands.command()
    async def setup(self, ctx: Context, name: str):
            
        if not name.isalnum():
                namesub = name.replace("-", "")
                if not namesub.isalnum():
                    await ctx.send("Only valid characters include letters, numbers, and `-`")
                    return 

        self.db.upsert({'guildId': ctx.guild.id, 'domainprefix': name}, where('guildId' == ctx.guild.id))
        await ctx.send(f"Changed this server's prefix to {name}")
