import discord
from discord.ext import commands
from discord.ext.commands import context
import asyncio
class MyHelp(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
    # async def send_bot_help(self, mapping):
    #     filtered = await self.filter_commands(self.context.bot.commands, sort=True)
    #     names = [command.name for command in filtered]
    #     available_commands = "\n".join(names)
    #     embed  = discord.Embed(description=available_commands)
    #     await self.context.send(embed=embed)
    #     await self.context.send("This is the help page for a command")
    @commands.command()
    async def help(self, ctx: context, command: str):
        if command == "create":

            def page1():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="FORMAT:", value="The format of the command is :", inline=True)
                embed.add_field(name="⠀", value=" **$create `name`  `type`  `env`** ", inline=True)
                return embed
            def page2():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="TYPE:", value="There are currently 4 supported types:", inline=True)
                embed.add_field(name="⠀", value="`vanilla`  `custom`  `paper`  `bukkit`", inline=True)
                return embed
            def page3():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="PRESETS:", value="Copy and paste if you just want these", inline=False)
                embed.add_field(name="⠀", value="""
                \n\n**Pure Vanilla, Latest Version:** \n`$create name vanilla MAX_MEMORY=3` \n
                **Vanilla running on paper, Latest Version:** \n`$create name paper MAX_MEMORY=3` \n
                **Manhunt paper server, Latest Version:** \n`$create name paper MAX_MEMORY=4,SPIGET_RESOURCES=86708`\n
                *info on how to use the plugin at https://www.spigotmc.org/resources/manhunt-1-16x-1-19x.86708/*\n
                
                
                """, inline=True)
                return embed
            def page4():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="ENV FORMAT:", value="Must be in all caps and have no spaces, If multiple values, seperate using `|` (Shift + Backslash ( \\ ) )", inline=False)
                embed.add_field(name="⠀", value="`ENV1=value,ENV2=value1|value2`", inline=False)
                return embed
            def page5():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="Global Environmental Variable Options", value="`VERSION`: *Minecraft version, default is latest. Example:* **1.19.1**", inline=True)
                embed.add_field(name="⠀", value="`MAX_MEMORY`: *RAM allocated, valid range is between 2 and 8. Example:* **4**", inline=True)
                return embed
            def page6():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="Variables for: Custom, Paper, Spigot, Bukkit \n", value= """`ICON`: *The server icon. \n
                Example:* **https://i.imgur.com/m7mVx9q.png** \n
                `WORLD` *Link to the world file (.zip) \n
                 Example:* **https://www.minecraftmaps.com/parkour-maps/reef-race/download-map**\n
                `DATAPACKS` *Link to the datapacks (.zip). \n
                Example:* **https://static.planetminecraft.com/files/resource_media/datapack/manhunt-v1-1.zip**\n
                `VANILLATWEAKS_SHARECODE`: *The code for a vanillatweaks datapack set (no #).* \n
                *Example:* **JQ5B97** \n
                `SPIGET_RESOURCES`: *Spigot plugins, use the last numbers in the link as the code* \n
                *Example:* **60837** \n
                """, inline=True)
                return embed
            def page7():
                embed=discord.Embed(title="⠀", color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="EXAMPLES", value="""
                `$create mysmp paper MAX_MEMORY=4,VERSION=1.16.2,ICON=i.imgur.com/m7mVx9q.png,DATAPACKS=static.planetminecraft.com/files/resource_media/datapack/manhunt-v1-1.zip` \n
                *creates a 1.16.2 paper server with the icon as the picture and the manhunt datapack from planetminecraft\n*
                `$create mysmp paper VERSION=1.16.2,MAX_MEMORY=4,SPIGET_RESOURCES=86708|68517`\n
                *creates a 1.16.2 paper server with the spigot plugin 68517 (Villager Optimiser) AND 86708 (Dream Manhunt)*
                
                """, inline=True)
                embed.add_field(name="⠀", value="⠀", inline=True)
                embed.add_field(name="⠀", value="Note: If you do not want to set an env variable, you do not need to include it at all", inline=False)
                embed.set_footer(text='Can change other variables like SPAWN_PROTECTION in the "$set" command. "$help set" to learn more')
                embed.set_footer(text='⠀')
                return embed
            # def page1():
            #     embed=discord.Embed(title="⠀", color=0x3cf00f)
                
            #     embed.set_footer(text='⠀')
            #     return embed
            

            pages = [page1(), page2(), page3(), page4(), page5(), page6(), page7()]
            currentpage = 0
            message = await ctx.send(embed=pages[currentpage])
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=120, check=check)
                    if str(reaction.emoji) == "▶️":
                        try:
                            await message.edit(embed=pages[currentpage+1])
                            await message.remove_reaction(reaction, user)
                            currentpage+=1
                        except: 
                            await message.remove_reaction(reaction, user)
                            pass
                    elif str(reaction.emoji) == "◀️":
                        try:
                            await message.edit(embed=pages[currentpage-1])
                            await message.remove_reaction(reaction, user)
                            currentpage-=1
                        except: 
                            await message.remove_reaction(reaction, user)
                            pass
                except asyncio.TimeoutError:
                    await message.delete()
                    break
            