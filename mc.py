from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where

class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)

    @commands.command()
    async def create(self, ctx: Context, name: str):

        if self.get(ctx, name, ):
            await ctx.send('Server with name already exists.')
            return
        mctype = mcversion = seed = memory = ops = whitelist = ftb = forgeapi = difficulty = spawnprot = viewdistance = maxbuild = hardcore = commandblock = maxworldsize = maxplayers = motd = enforcewhitelist = world = modpack = vanillatweaks = spigotresources = datapacks = None
        self.db.insert({
            #main params
            'serverId': ctx.guild.id,
            'name': name,
            'type': mctype,
            'version': mcversion,
            'seed': seed,
            'memory': memory,
            #users
            'ops': ops,
            'whitelist': whitelist
            #modded
            'ftb': ftb,
            #forge modded
            'forgeapi': forgeapi,
            #server properties
            'difficulty': difficulty,
            'spawnprot': spawnprot
            'viewdistance': viewdistance,
            'maxbuild': maxbuild,
            'hardcore': hardcore,
            'commandblock': commandblock,
            'maxworldsize': maxworldsize,
            'maxplayers': maxplayers,
            'motd': motd,
            'enforcewhitelist': enforcewhitelist
            #links
            'world': world,
            'modpack': modpack,
            'vanillatweaks': vanillatweaks,
            'spigotresources': spigotresources,
            'datapacks': datapacks


        })
        await ctx.send(f'Server with name "{name}" added.')

    @commands.command()
    async def delete(self, ctx: Context, name: str):
        ids = self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
        if len(ids) == 0:
            await ctx.send('Server does not exist.')
            return
        await ctx.send(f'Server with name "{name}" deleted.')

    @commands.command()
    async def list(self, ctx: Context):
        servers = [entry['name'] for entry in self.get(ctx)]
        if len(servers) == 0:
            await ctx.send('No servers')
            return
        await ctx.send('\n'.join(servers))


    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            return self.db.get((where('serverId') == id) & (where('name') == name))
        else:
            return self.db.search((where('serverId') == id))
