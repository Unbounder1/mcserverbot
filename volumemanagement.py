import discord
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, where, Query
from mc import MC
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()
botowners = os.getenv('BOT_OWNERS').split(',')
class ManageVolumes(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)
        self.conf = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)
        self.backups = TinyDB('serverDB.json').table(name='_volumes', cache_size = 0)
    @commands.command()
    async def oldworlds(self, ctx: Context, function = "list", worldname = None, newowner = None):
        if function == "list":
            worldlist = self.backups.search((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id))
            if len(worldlist) == 0:
                await ctx.send("You have no old worlds")
                return
            listoutput = []
            for i in range(0,len(worldlist)):
                worlds = worldlist[i]['description']
                if len(worldlist[i]['description']) > 20:
                    worlds = worlds[:20] + "..."
                listoutput.append(worldlist[i]['worldname'] + ": " + worlds)
            await ctx.send('\n'.join(listoutput))
        elif function == "info":
            worldlist = self.backups.get((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
            if len(worldlist) == 0:
                await ctx.send(f"Old world {worldname} not found")
                return
            await ctx.send("Worldname: **" + worldlist['worldname'] + "** \nDescription: *" + worldlist['description'] + "*\nType: *" + worldlist['type'] + "*\nVersion:" + worldlist['version'])
        elif function == "delete":
            ids = self.backups.get((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
            print (ids)
            if len(ids) == 0:
                await ctx.send("World not found")
            def check(m): 
                return m.author == ctx.author and m.channel == ctx.channel
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
                self.backups.remove((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
                await ctx.send(f"World {worldname} has been deleted")
                return
        elif function == "transfer":
            owner = newowner.replace("<","")
            owner = owner.replace(">","")
            owner = owner.replace("@","")
            owner = owner.replace("!","")
            owner = int(owner)
            def check(m): 
                return m.author.id == int(owner) and m.channel == ctx.channel
            try: 
                message = await ctx.send(f"Are you sure you want to transfer the ownership to <@{owner}>? To confirm, have THEM type (y)es. If no, type anything else. \nCancelling in 30 seconds")
                response = await self.bot.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError: 
                await message.edit(content = f"<@{owner}> did not reply in time. Please try again")
                return
            if response.content.lower() not in ("yes", "y"):
                await ctx.send(f"<@{owner}> did not accept the transfer request.")
                return
            else:
                querycheck = Query()
                maxworlds = self.conf.get(querycheck.guildId == ctx.guild.id)['maxworlds']
                currentactive = len(self.db.search((querycheck.owner == ctx.author.id) & (querycheck.guildId == ctx.guild.id)))
                if len(self.backups.search((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id))) + currentactive >= maxworlds:
                    if str(ctx.author.id) not in botowners:
                        await ctx.send(f"You can only have {maxworlds} worlds (including active servers)")
                        return
                self.backups.update({'owner': owner}, (where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
                await ctx.send(f"Successfully transferred {worldname} to <@{owner}>")
            