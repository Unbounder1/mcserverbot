import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from mc import MC
from setupcommands import setup
from helpcommands import MyHelp
load_dotenv()

CLIENT_TOKEN = os.getenv('CLIENT_TOKEN')


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='$', help_command=None, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False),intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

bot.add_cog(setup(bot))
bot.add_cog(MC(bot))
bot.add_cog(MyHelp(bot))
bot.run(CLIENT_TOKEN)
