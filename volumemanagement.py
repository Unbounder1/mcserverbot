import discord
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, where
from mc import MC
import asyncio
class ManageVolumes(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_volumes', cache_size = 0)
    
    @commands.command()
    async def oldworlds(self, ctx: Context, function = "list", worldname = None):
        if function == "list":
            worldlist = self.db.search((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id))
            if len(worldlist) == 0:
                await ctx.send("You have no old worlds")
            listoutput = []
            for i in range(0,len(worldlist)):
                worlds = worldlist[i]['description']
                if len(worldlist[i]['description']) > 20:
                    worlds = worlds[:20] + "..."
                listoutput.append(worldlist[i]['worldname'] + ": " + worlds)
            await ctx.send('\n'.join(listoutput))
        elif function == "info":
            worldlist = self.db.get((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
            if len(worldlist) == 0:
                await ctx.send(f"Old world {worldname} not found")
                return
            await ctx.send("Worldname: **" + worldlist['worldname'] + "** \nDescription: *" + worldlist['description'] + "*\nType: *" + worldlist['type'] + "*\n  ")
        elif function == "delete":
            ids = self.db.get((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
            if len(ids) == 0:
                await ctx.send("World not found")
            def check(message): 
                return message.author == ctx.author and message.channel == ctx.channel
            try: 
                await ctx.send("Are you sure you want to delete the world (There is no going back):\nTo confirm type (y)es. If no, type anything else")
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError: 
                return
            if response.content.lower() not in ("yes", "y"):
                message = await ctx.send("Cancelling deletion...")
                await message.edit(content = "Deletion has been cancelled")
                return
            else: 
                self.db.remove((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
                await ctx.send(f"World {worldname} has been deleted")
                return