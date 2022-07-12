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
    async def help(self, ctx: context, command = "all", currentpage = 1):
        if command == "all":
            def page1():
                embed=discord.Embed(color=0x00ffff)
                embed.set_author(name="Main Help Page")
                embed.add_field(name="List of active commands", value="""
                `$create` Creating a server. See more info at $help create \n
                `$set` Setting OPTIONS of a server, like the ones in server.properties. See more info at $help set \n
                `$addmoderator` `servername` `@user` : Adds user to the minecraft server moderator list \n
                `$removemoderator` `servername` `@user` : Removes a user to the minecraft server moderator list \n
                `$start` `servername` : Starts the specified server \n
                `$stop` `servername` : Stops the specified server (Need to be a moderator of the minecraft server) \n
                `$addplayer` `servername` `whitelist/ops` `ingamename1,ingamename2` : Adds listed users to the whitelist/ops list \n
                `$removeplayer` `servername` `whitelist/ops` `ingamename1,ingamename2` : Removes listed users to the whitelist/ops list **NOT IMPLEMENTED YET** \n""", inline = True)
                return embed
            def page2():
                embed=discord.Embed(color=0x00ffff)
                embed.add_field(name="List of info commands", value="""
                `$info` `servername` : Gets info of the server, like the name, type, and options that were set. \n
                `$listmoderator` `servername` : Lists all moderators **NOT IMPLEMENTED YET** \n
                `$status` `servername` : Lists the status of the specified server \n
                `$ip` `servername` : Gets the IP of the specified server \n""", inline=True)
                return embed
            pages = [page1(), page2()]
            await self.pageturner(ctx,currentpage,pages)

        elif command == "create":

            def page1():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="FORMAT:", value="""The format of the command is :\n
                **$create `name`  `type`  `options`**\n
                There are currently 4 supported types:\n
                `vanilla`  `custom`  `paper`  `bukkit`\n \n
                
                """, inline=True)
                embed.add_field(name="OPTIONS FORMAT:", value="Must be in all caps and have no spaces. \nIf multiple values, seperate using `|` (Shift + Backslash ( \\ ) ) \n\n`OPTION1=value,OPTION2=value1|value2`", inline=False)
                return embed
            def page2():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 2/5")
                embed.add_field(name="PRESETS:", value="Copy and paste if you just want these", inline=False)
                embed.add_field(name="⠀", value="""
                \n\n**Pure Vanilla, Latest Version:** \n`$create name vanilla MAX_MEMORY=3` \n
                **Vanilla running on paper, Latest Version:** \n`$create name paper MAX_MEMORY=3` \n
                **Manhunt paper server, Latest Version:** \n`$create name paper MAX_MEMORY=4,SPIGET_RESOURCES=86708`\n
                *info on how to use the manhunt plugin at https://www.spigotmc.org/resources/manhunt-1-16x-1-19x.86708/*\n
                
                """, inline=True)
                return embed
            def page3():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 3/5")
                embed.add_field(name="Global Options (All types have these)", value="`VERSION`: *Minecraft version, default is latest. Example:* **1.19.1**", inline=False)
                embed.add_field(name="⠀", value="`MAX_MEMORY`: *Amount of RAM the server will have, valid range is between 2 and 8. 4 is enough for almost anything normal. If you need more, please contact a bot owner. Example:* **4**", inline=False)
                return embed
            def page4():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 4/5")
                embed.add_field(name="Options for: Custom, Paper, Spigot, Bukkit \n", value= """`ICON`: *Image of the server icon. \n
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
            def page5():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 5/5")
                embed.add_field(name="EXAMPLES", value="""
                `$create mysmp paper MAX_MEMORY=4,VERSION=1.16.2,ICON=i.imgur.com/m7mVx9q.png,DATAPACKS=static.planetminecraft.com/files/resource_media/datapack/manhunt-v1-1.zip` \n
                *creates a 1.16.2 paper server with the icon as the picture and the manhunt datapack from planetminecraft*\n
                `$create mysmp paper VERSION=1.16.2,MAX_MEMORY=4,SPIGET_RESOURCES=86708|68517`\n
                *creates a 1.16.2 paper server with the spigot plugin 68517 (Villager Optimiser) AND 86708 (Dream Manhunt)*
                
                """, inline=True)
                embed.add_field(name="⠀", value="⠀", inline=True)
                embed.add_field(name="⠀", value="Note: If you do not want to set an option, you do not need to include it at all", inline=False)
                embed.set_footer(text='Can change other options like SPAWN_PROTECTION in the "$set" command. "$help set" to learn more')
                embed.set_footer(text='⠀')
                return embed
            # def page1():
            #     embed=discord.Embed(color=0x3cf00f)
                
            #     embed.set_footer(text='⠀')
            #     return embed
            

            pages = [page1(), page2(), page3(), page4(), page5()]
            await self.pageturner(ctx,currentpage,pages)
    # @help.error
    # async def indexerror(self, ctx: context, error):
    #     if isinstance(error, commands.CommandError):
    #         await ctx.send("That is not a valid page")
    #         return
    #     elif isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("Check your arguments")
    #         return
    async def pageturner(self, ctx: context, currentpage: int, pages):
        currentpage -=1
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
                #await message.delete()
                break