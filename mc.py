from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from pysondb import db

class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db.getDb('serverDB.json')
        self.db.add({
            'serverId': 'discordServerId',
            'mcName': 'mcServerName'
        })

    @commands.command()
    async def create(self, ctx: Context, name: str):

        if self.get(ctx, name):
            await ctx.send('Server with name already exists.')
            return

        self.db.add({
            'serverId': ctx.guild.id,
            'mcName': name
        })
        await ctx.send(f'Server with name "{name}" added.')

    @commands.command()
    async def delete(self, ctx: Context, name: str):

        if not self.get(ctx, name):
            await ctx.send('Server does not exist.')
            return

        self.db.deleteById(self.getId(ctx, name))
        await ctx.send(f'Server with name "{name}" deleted.')

    @commands.command()
    async def list(self, ctx: Context):
        servers = [entry['mcName'] for entry in self.get(ctx)]
        await ctx.send('\n'.join(servers))


    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            res = self.db.getBy({'serverId': id, 'mcName': name})
        else:
            res = self.db.getBy({'serverId': id})
        if len(res) == 0: return None
        return res

    def getId(self, ctx: Context, name: str = None):
        res = self.get(ctx, name)
        if res == None: return res
        return res[0]['id']
