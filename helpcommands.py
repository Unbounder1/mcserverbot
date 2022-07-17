import discord
from discord.ext import commands
from discord.ext.commands import Context
from difflib import SequenceMatcher
import asyncio
class MyHelp(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
    @commands.command()
    async def help(self, ctx: Context, command = "all", *, args= None):
        if not args:
            currentpage = 1
        
        if command == "all":
            def page1():
                embed=discord.Embed(color=0x0bf4e9)
                embed.set_author(name="Help Page")
                embed.add_field(name="List of active commands", value="""
                `$help all` : Displays this message\n
                `$help create` : Displays info on how to use $create\n
                `$help set` : Displays info on how to use $set\n
                `$help search` : Displays info on specific options in $set\n
                `$help delete` : Displays info on how to use $delete\n
                `$help oldworlds` : Displays info on how to manage old worlds\n
                \nGo to the next page for the Main Help Page\n
                """, inline = True)
                return embed
            def page2():
                embed=discord.Embed(color=0x0bf4e9)
                embed.set_author(name="Main Help Page")
                embed.add_field(name="List of active commands", value="""
                `$create` : Creating a server. See more info at $help create \n
                `$set` : Setting OPTIONS of a server, like the ones in server.properties. See more info at $help set \n
                `$addmoderator` `servername` `@user` : Adds user to the minecraft server moderator list \n
                `$removemoderator` `servername` `@user` : Removes a user to the minecraft server moderator list \n
                `$start` `servername` : Starts the specified server \n
                `$stop` `servername` : Stops the specified server (Need to be a moderator of the minecraft server) \n
                \nGo to the next page for options
                """, inline = True)
                return embed
            def page3():
                embed=discord.Embed(color=0x0bf4e9)
                embed.add_field(name="List of active commands", value="""
                `$addplayer` `servername` `whitelist/ops` `ingamename1,ingamename2` : Adds listed users to the whitelist/ops list \n
                `$removeplayer` `servername` `whitelist/ops` `ingamename1,ingamename2` : Removes listed users to the whitelist/ops list **NOT IMPLEMENTED YET** \n
                `$delete` : deleting a server. See more info and options at $help delete \n
                `$transfer` `servername` `@user` : Transfer ownership of a server to another user
                \nGo to the next page for options
                """, inline = True)
                return embed
            def page4():
                embed=discord.Embed(color=0x0bf4e9)
                embed.add_field(name="List of info commands", value="""
                `$info` `servername` : Gets info of the server, like the name, type, and options that were set. \n
                `$listmoderator` `servername` : Lists all moderators **NOT IMPLEMENTED YET** \n
                `$status` `servername` : Lists the status of the specified server \n
                `$ip` `servername` : Gets the IP of the specified server \n
                \nGo to the next page for options
                """, inline=True)
                return embed
            def page5():
                embed=discord.Embed(color=0x3cf00f)
                embed.add_field(name="List of world management commands", value="""
                `$oldworlds` `list` : Lists all the world backups you have \n
                `$oldworlds` `info` `worldname` : Get more info on specific world backup \n
                `$oldworlds` `delete` `worldname` : Permanently delete the world \n
                `$oldworlds` `transfer `worldname` `@usertotransferto` : Transfer world to another user \n
                `$restore` `worldname` name=`newservername`,version=`version|(empty = latest version)` \n
                \nGo to the next page for options
                """, inline=True)
                return embed

            pages = [page1(), page2(), page3(), page4(), page5()]
            await self.pageturner(ctx,currentpage,pages)

        elif command == "create":

            def page1():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="How to create a Minecraft server with this bot")
                embed.add_field(name="FORMAT:", value="""The format of the command is :\n
                **$create `name`(one word, alphabet only)  `type`  `options`**\n 
                There are currently 4 supported types:\n
                `vanilla`  `custom`  `paper`  `bukkit`\n \n
                
                """, inline=True)
                embed.add_field(name="OPTIONS FORMAT:", value="""
                Must be in **all caps** and have **no spaces**. \n
                If multiple values, seperate using `|` (Shift + Backslash ( \\ ) ) \n\n
                `OPTION1=value,OPTION2=value1|value2`
                \nGo to the next page for info on options
                
                """, inline=False)
                return embed
            def page2():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 2/6")
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
                embed.set_author(name="Page 3/6")
                embed.add_field(name="Global Options (All types have these)", value="`VERSION`: *Minecraft version, default is latest. Example:* **1.19.1**", inline=False)
                embed.add_field(name="⠀", value="""`MAX_MEMORY`: *Amount of RAM the server will have, valid range is between 2 and 8. 4 is enough for almost anything normal. If you need more, please contact a bot owner. Example:* **4**
                \n`MOTD`: The server message. Use (§) as formatting codes, and input the motd in between quotes: Example: "This is the §c§lMOTD"
                
                
                
                """, inline=False)
                return embed
            def page4():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 4/6")
                embed.add_field(name="Options for: Custom, Paper, Spigot, Bukkit \n", value= """`ICON`: *Image of the server icon. \n
                Example:* **https://i.imgur.com/m7mVx9q.png** \n
                `VANILLATWEAKS_SHARECODE`: *The code for a vanillatweaks datapack set (no #).* \n
                *Example:* **JQ5B97** \n
                `SPIGET_RESOURCES`: *Spigot plugins, use the last numbers in the link as the code* \n
                *Example:* **60837** \n
                """, inline=True)
                return embed
            def page5():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 5/6")
                embed.add_field(name="Continued...\n", value= """
                `WORLD` *Link to the world file (.zip) \n
                 Example:* **https://www.minecraftmaps.com/parkour-maps/reef-race/download-map**\n
                `DATAPACKS` *Link to the datapacks (.zip). \n
                Example:* **https://static.planetminecraft.com/files/resource_media/datapack/manhunt-v1-1.zip**\n
                \nIf you want to use your own files, I suggest uploading them to either anonfiles.com, filechan.com, or something like that. Drive wont work because the link will say "Are you sure" or something about viruses and the bot wont like that
                The download link must directly link to the download, so when you enter the link it automatically downloads the file.
                To do this, for the suggestions above, right click the download button and click copy link. To verify, paste it in the browser and see if it downloads automatically
                """, inline=True)
                return embed
            def page6():
                embed=discord.Embed(color=0x3cf00f)
                embed.set_author(name="Page 6/6")
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
            

            pages = [page1(), page2(), page3(), page4(), page5(), page6()]
            await self.pageturner(ctx,currentpage,pages)
        elif command == "set":
            if not args:
                embed=discord.Embed(color=0x0bf4e9)
                embed.add_field(name="Setting Variable Format", value="""
                The format for the command is $set servername OPTION1,OPTION2\n
                To see info on all the options, type `$set search all` or `$set search keyword`""", inline=True)
                await ctx.send(embed=embed)
                return
        elif command == "search":
            finalstring = "⠀\n\n**OPTIONS:**\n\n"
            with open('mcenvvars.txt') as file:
                content = file.readlines()
            if args == "all":
                length = int(len(content)/2)
                with open("mcenvvars.txt") as file:
                    await ctx.send(file=discord.File(file, 'mcenvvars.txt'))
                return
            for eachline in content:
                for eachword in eachline.split(" "):
                    eachword = eachword.lower()
                    if SequenceMatcher(a=args.lower(),b=eachword).ratio() > 0.7:
                        finalstring = finalstring + '\n' + eachline
                        break
                    elif (eachword.find(args.lower()) != -1):
                        finalstring = finalstring + '\n' + eachline 
                        break
            embed=discord.Embed(color=0x0bf4e9)
            embed.add_field(name=f'What I found for "{args}"', value=finalstring, inline=True)
            await ctx.send(embed=embed)
            return
        elif command == "delete":
            def page1():
                embed=discord.Embed(color=0x0bf4e9)
                embed.set_author(name="How to use the DELETE command")
                embed.add_field(name="Saving the world for later use, backup, etc:", value="""Page 1/2 \n
                $delete name true backupworldname "world description so that you can remember what the world was later"\n
                ie. `$delete myserver true duosurvivalsmp "An SMP that I duoed with someone. Ended due to inactivity, but has some pretty cool builds"`\n
                *must be the owner of the minecraft server to be able to delete it*
            """, inline=True)
                return embed
            def page2():
                embed=discord.Embed(color=0x0bf4e9)
                embed.set_author(name="Main Help Page")
                embed.add_field(name="Permanently deleting the world:", value="""Page 2/2 \n
                $delete name , and then type y or yes to confirm when prompted\n
                ie. `$delete myserver`\n
                *must be the owner of the minecraft server to be able to delete it*
            """, inline=True)      
                return embed
            pages = [page1(),page2()]
            await self.pageturner(ctx,currentpage,pages)
        elif command == "oldworlds":
            def page1():
                embed=discord.Embed(color=0x3cf00f)
                embed.add_field(name="List of world management commands", value="""Page 1/1 \n
                `$oldworlds` `list` : Lists all the world backups you have
                `$oldworlds` `info` `worldname` : Get more info on specific world backup
                `$oldworlds` `delete` `worldname` : Permanently delete the world
                `$oldworlds` `transfer` `worldname` `@user` : Transfer world to another user
                `$restore` `worldname` name=`newservername`,version=`version|(empty = latest version)`

                """, inline=True)
                return embed
            pages = [page1()]
            await self.pageturner(ctx,currentpage,pages)
    @commands.command()
    async def helpsetup(self, ctx: Context):
        embed=discord.Embed(color=0x3cf00f)
        embed.set_author(name="Welcome to Atern-ative!⠀\n⠀")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/996965755524501614/998104400981659658/blurtrails.Redshift_ROP1.00010.png")
        embed.set_image(url="https://cdn.discordapp.com/attachments/998113234257191053/998113763624501248/unknown.png")
        embed.set_footer(text='Image is from /visit kwuo on hypixel housing no cap good idea very fun. ')
        embed.add_field(name="Info about this bot!\n⠀", value="""
        This bot uses my servers to host mc servers!
        That means that this is coming out of my energy bill smile \n
        **-bot use-**\n
        This bot allows users to create their own minecraft servers without the annoying wait and lag of aternos 
        \n**-other info-**\n
        Supports vanilla, paper, bukkit
        No modded rn because i too lazy
       \n**-how to start-**\n
        To start using this bot, type **$help**! \n
        **Start Minecrafting!!!!!**
        """, inline=False)
        await ctx.send(embed=embed)
    @help.error
    async def indexerror(self, ctx: Context, error):
        if isinstance(error, commands.CommandError):
            await ctx.send("That is not a valid page")
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Check your arguments")
            return
    async def pageturner(self, ctx: Context, currentpage: int, pages):
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