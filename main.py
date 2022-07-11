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
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')


bot.add_cog(setup(bot))
bot.add_cog(MC(bot))
bot.help_command = MyHelp()
bot.run(CLIENT_TOKEN)
