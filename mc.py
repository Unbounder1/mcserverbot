from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where

class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)

    @commands.command()
    async def create(self, ctx: Context, name: str, mctype: str=None, mcversion: str=None, memory: str=2):

        if self.get(ctx, name):
            await ctx.send('Server with name already exists.')
            return

        #self.db.insert({
        #    'serverId': ctx.guild.id,
        #    'name': name,

        #})
        await ctx.send(f'Server with name "{name}" added.')
        seed = ops = whitelist = ftb = forgeapi = servername = difficulty = spawnprot = viewdistance = maxbuild = hardcore = commandblock = maxworldsize = maxplayers = motd = enforcewhitelist = world = modpack = vanillatweaks = spigetresources = datapacks = icon = None
        #mandatory things
        defaultenv = {
                'GUI': "false", 
                'EULA': "true", 
                'INIT_MEMORY': "1G",

                'OVERRIDE_SERVER_PROPERTIES' : "true", 
                'REPLACE_ENV_IN_PLACE': "false",
                'OVERRIDE_OPS': "false",
                
                #RCON
                'ENABLE_RCON': "true",
                'RCON_PASSWORD': "minecraft", #Advised to change this
                #autopause stuff
                'MAX_TICK_TIME' : "-1",
                'ENABLE_AUTOPAUSE': "true",
                'AUTOPAUSE_TIMEOUT_EST': "3600",

                #autostop stuff
                'ENABLE_AUTOSTOP': "TRUE",
                'AUTOSTOP_TIMEOUT_EST': "172800" # 2 days

        }
        mainenv = {'TYPE': mctype, 'VERSION': mcversion,'MAX_MEMORY': memory}
        intpropenv = {'SEED': seed,'SPAWN_PROTECTION': spawnprot,'VIEW_DISTANCE': viewdistance,'MAX_BUILD_HEIGHT': maxbuild,'MAX_WORLD_SIZE': maxworldsize,'MAX_PLAYERS': maxplayers}
        strpropenv = {'OPS': ops,'SERVER_NAME': servername,'MOTD': motd}
        specialpropenv = {'DIFFICULTY': difficulty, 'world': world,'VANILLATWEAKS_SHARECODE': vanillatweaks,'DATAPACKS': datapacks,'SPIGET_RESOURCES': spigetresources, 'ICON': icon,'WHITELIST': whitelist}
        boolpropenv = {'ENABLE_COMMAND_BLOCK': commandblock,'HARDCORE': hardcore}
        #add modpack stuff later --------------------------
    #@commands.command()
    #async def set(self, ctx: Context, name: str):


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
