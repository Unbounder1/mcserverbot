import discord
from discord.ext import commands

class MyHelp(commands.HelpCommand):

    async def send_bot_help(self, mapping):
        filtered = await self.filter_commands(self.context.bot.commands, sort=True)
        names = [command.name for command in filtered]
        available_commands = "\n".join(names)
        embed  = discord.Embed(description=available_commands)
        await self.context.send(embed=embed)
        await self.context.send("This is the help page for a command")
    async def send_command_help(self, command):
        if command.name == "create":
            embed=discord.Embed(title="⠀", color=0x3cf00f)
            embed.set_author(name="How to create a Minecraft server with this bot")
            embed.add_field(name="FORMAT:", value="⠀", inline=False)
            embed.add_field(name="The format of the command is :", value="⠀", inline=False)
            embed.add_field(name="⠀", value=" **$create `name`  `type`  `env`** ", inline=False)
            embed.add_field(name="⠀", value="⠀", inline=False)
            embed.add_field(name="TYPE:", value="⠀", inline=False)
            embed.add_field(name="There are currently 4 supported types:", value="⠀", inline=False)
            embed.add_field(name="⠀", value="`vanilla`  `custom`  `paper`  `bukkit`", inline=False)
            embed.add_field(name="⠀", value="⠀", inline=False)
            embed.add_field(name="ENV FORMAT:", value="Must be in all caps and have no spaces, If multiple values, seperate using `|` (Shift + Backslash ( \\ ) )", inline=False)
            embed.add_field(name="⠀", value="`ENV1=value,ENV2=value1|value2`", inline=False)
            embed.add_field(name="⠀", value="⠀", inline=False)
            embed.add_field(name="ENV OPTIONS:", value="*valid env options*", inline=False)
            embed.add_field(name="⠀", value="`VERSION`: *Minecraft version, default is latest. Example:* **1.19.1**", inline=False)
            embed.add_field(name="⠀", value="`MAX_MEMORY`: *RAM allocated, valid range is between 2 and 8. Example:* **4**", inline=False)
            embed.add_field(name="⠀", value="All the ones down here are not in the vanilla type", inline=False)
            embed.add_field(name="⠀", value="`ICON`: *The server icon. Example:* **https://i.imgur.com/m7mVx9q.png**", inline=False)
            embed.add_field(name="⠀", value="`WORLD` *Link to the world file (.zip) Example:* ", inline=False)
            embed.add_field(name="⠀", value="`DATAPACKS` *Link to the datapacks (.zip). Example:* ", inline=False)
            embed.add_field(name="⠀", value="`VANILLATWEAKS_SHARECODE`: *The code for a vanillatweaks datapack set (no #).* ", inline=False)
            embed.add_field(name="⠀", value="*Example:* **JQ5B97** ", inline=False)
            embed.add_field(name="⠀", value="`SPIGET_RESOURCES`: *Spigot plugins, use the last numbers in the link as the code* ", inline=False)
            embed.add_field(name="⠀", value="*Example:* **60837**", inline=False)
            embed.add_field(name="⠀", value="⠀", inline=False)
            embed.add_field(name="⠀", value="⠀", inline=False)
            embed.add_field(name="EXAMPLE:", value="`$create mysmp paper MAX_MEMORY=4,VERSION=1.16.2,ICON=i.imgur.com/m7mVx9q.png,DATAPACKS=static.planetminecraft.com/files/resource_media/datapack/manhunt-v1-1.zip,SPIGET_RESOURCES=60837|39422|38295|23842`", inline=True)
            embed.set_footer(text='Can change other variables like SPAWN_PROTECTION in the "$set" command. "$help set" to learn more')
            message = await self.context.send(embed=embed)