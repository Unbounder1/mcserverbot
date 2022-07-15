from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from podman import PodmanClient
from time import sleep
import sys
import traceback
import asyncio
import nest_asyncio
nest_asyncio.apply()
import podscript
import cloudscript
from dotenv import load_dotenv
import os
load_dotenv()

uri = os.getenv('URI')
CLIENT_TOKEN = os.getenv('VIRUSTOTAL_TOKEN')
botowners = os.getenv('BOT_OWNERS').split(',')
class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)
        self.conf = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)
        self.backups = TinyDB('serverDB.json').table(name='_volumes', cache_size = 0)
        self.defaultenv = {
                    'GUI': "false", 
                    'EULA': "true", 
                    'INIT_MEMORY': "1G",

                    'OVERRIDE_SERVER_PROPERTIES' : "true", 
                    'REPLACE_ENV_IN_PLACE': "false",
                    'OVERRIDE_OPS': "false",
                    'OVERRIDE_WHITELIST': "false",
                    'REMOVE_OLD_DATAPACKS': 'true',
                    'ENABLE_ROLLING_LOGS': "false",
                    
                    #RCON
                    'ENABLE_RCON': "true",
                    'RCON_PASSWORD': "minecraft", #Advised to change this
                    #autopause stuff

                    'MAX_TICK_TIME' : "-1",
                    'ENABLE_AUTOPAUSE': "true",
                    'AUTOPAUSE_TIMEOUT_EST': "3600",
                    'AUTOPAUSE_KNOCK_INTERFACE' : "tap0",

                    #autostop stuff
                    'ENABLE_AUTOSTOP': "false",
                    'AUTOSTOP_TIMEOUT_EST': "172800" # 2 days
            }
    @commands.command()
    async def create(self, ctx: Context, name: str, mctype = "vanilla", *, args = '0'):
        
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if self.get(ctx, name):
            await ctx.send('Server with name already exists.')
            return
        if name == "help":
            await ctx.send("Did you mean $help create?")
            return
        querycheck = Query()
        maxperuser = self.conf.get(querycheck.guildId == ctx.guild.id)['maxperuser']
        maxservers = self.conf.get(querycheck.guildId == ctx.guild.id)['maxservers']
        maxworlds = self.conf.get(querycheck.guildId == ctx.guild.id)['maxworlds']
        currentactive = len(self.db.search((querycheck.owner == ctx.author.id) & (querycheck.guildId == ctx.guild.id)))
        if currentactive>=maxperuser:
            if str(ctx.author.id) not in botowners:
                await ctx.send(f"You can only have {maxperuser} servers active per person")
                return
        if len(self.backups.search((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id))) + currentactive >= maxworlds:
            if str(ctx.author.id) not in botowners:
                await ctx.send(f"You can only have {maxperuser} servers active per person")
                return
        if len(self.db.search((querycheck.status == 'up') & (querycheck.guildId == ctx.guild.id)))>=maxservers:
            if str(ctx.author.id) not in botowners:
                await ctx.send(f"This server can only have {maxservers} servers up at once")
                return
        message = await ctx.send("Attempting to create the world (may take a few minutes if you used a link)...")
        mainenv = {'VERSION': None,'MAX_MEMORY': None,'MOTD': "A minecraft server created by the Voark bot"}
        #__setting up the universal env variables__
        if len(args)>0 and args!="0":
            argslist = args.split(",")
            for a in argslist:
                temp = a.split("=")
                if temp[0] == "MAX_MEMORY":
                    try:
                        if 2<=int(temp[1])<=8: #MIN/MAX MEMORY USAGE
                            mainenv[temp[0]]=str(temp[1]) + "G"
                        elif ctx.author.id in botowners:
                            mainenv[temp[0]]=str(temp[1]) + "G"
                        else:
                            raise OverflowError
                    except OverflowError:
                        await ctx.send("Memory can only be set between 2 and 8 gigabytes. Ask the bot owner if you need more")
                        return
                elif temp[0] == 'VERSION':
                    mainenv[temp[0]]=temp[1]
                elif temp[0] == 'MOTD':
                    mainenv[temp[0]]=temp[1].replace('"','')
        
        #__setting up the specific environmental variables__
        if mctype.lower() == "vanilla":
            env = {**self.defaultenv, **mainenv}
        elif (mctype.lower() == "custom") or (mctype.lower() == "paper") or (mctype.lower() == "bukkit") or (mctype.lower() == "spigot"):
            linkpropenv = dict.fromkeys(['DATAPACKS','ICON','WORLD'], None)
            otherpropenv = dict.fromkeys(['VANILLATWEAKS_SHARECODE','SPIGET_RESOURCES'], None)
            seed = None

            if len(args)>0 and args!="0":
                arglist = args.split(",")
                for a in arglist:
                    temp = a.split("=")
                    #__malware/validity checker for links
                    if temp[0] in linkpropenv:

                        analysis = await cloudscript.virustest(temp[1])
                        if analysis == '1':
                            linkpropenv[temp[0]]=temp[1]
                            await ctx.send("Check 1: Links are valid")
                        else:
                            await ctx.send(analysis)
                    elif temp[0] in otherpropenv:
                        otherpropenv[temp[0]]=temp[1]
                    elif temp[0] == "SEED":
                        seed = temp[1]
                    elif temp[0] in mainenv:
                        continue
                    else:
                        await ctx.send("Please check your spelling for " + temp[0])
                        return               
            if mctype.lower() == "custom":
                type = "VANILLA"
            else:
                type = mctype.upper()
            env = {**self.defaultenv, **mainenv, **linkpropenv, **otherpropenv, 'SEED': seed, 'TYPE': type}

        #__checking universal arguments__
        
        # if len(args)>0 and args!="0":
        #     arglist = args.split(",")
        #     for a in arglist:
        #         temp = a.split("=")
        #         if temp[0] in mainenv:
        #             mainenv[temp[0]]=temp[1]
        #         else:
        #             await ctx.send("Please check your spelling for " + temp[0])
        #             return


        #add modpack stuff later --------------------------

        port = None
        for p in range (int(os.getenv('PORT_MIN')),int(os.getenv('PORT_MAX'))):
            portchecker = Query()
            if self.db.contains(portchecker.port == p):
                continue
            else:
                port = p
                break
        owner = ctx.author.id
        moderators = []
        self.db.insert({
        'serverId': ctx.guild.id,
        'name': name,
        'port': port,
        'type': mctype,
        'owner': owner,
        'moderators': moderators,
        'status': 'down'
        })


        await message.edit(content = f'Server with name "{name}" on "{mctype}" added.')
        processname = name + "." + str(ctx.guild.id)

        #__starting the podman container__
        creation = await podscript.create(processname, env, port, mainenv['VERSION'])
        if creation==0:
            await ctx.send("Something went wrong. Check your spelling and try again")
            self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
            return
        
        finalip = await cloudscript.create(name, ctx.guild.id, port)

        #__sending server status messages__
        await self.startup(ctx,processname, finalip)
        self.db.update({'status': 'up'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
        return
    @commands.command()
    async def set(self, ctx: Context, name: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        await ctx.send("Attempting to set variables")
        processname = name + "." + str(ctx.guild.id)
        intpropenv = strpropenv = specialpropenv = boolpropenv = {}
        intpropenv = dict.fromkeys(['TYPE','SPAWN_PROTECTION','VIEW_DISTANCE','MAX_BUILD_HEIGHT','MAX_WORLD_SIZE','MAX_PLAYERS'])
        strpropenv = dict.fromkeys(['SERVER_NAME','MOTD','DIFFICULTY', 'MODE'], None)
        boolpropenv = dict.fromkeys(['ENABLE_COMMAND_BLOCK','HARDCORE','ENFORCE_WHITELIST', 'ALLOW_FLIGHT', 'ONLINE_MODE'], None)
        linkpropenv = dict.fromkeys(['DATAPACKS','ICON'], None)
        otherpropenv = dict.fromkeys(['VANILLATWEAKS_SHARECODE','SPIGET_RESOURCES'], None)
        maxmemory = {'MAX_MEMORY': None}
        env = {'intpropenv':intpropenv,'strpropenv':strpropenv,'boolpropenv':boolpropenv,'linkpropenv':linkpropenv,'otherpropenv':otherpropenv, 'maxmemory': maxmemory}


        oldenvlst = await podscript.findenv(processname)
        oldenvdict = {}
        #__converting the list output of 'podman inspect' to a dictionary format__
        for variables in oldenvlst:             
            templst = variables.split("=")
            oldenvdict[templst[0]] = templst[1]
        #__moving already set variables to empty env variables__
        for oldvariables in oldenvdict:
            for types in env:                       
                for variables in env[types]:
                    if oldvariables in env[types]:
                        env[types][oldvariables] = oldenvdict[oldvariables]
        
                        
        if len(args)>0: 
            arglist = args.split(",")
            for a in arglist:
                try:
                    temp = a.split("=")
                    if temp[0] in intpropenv:           
                        try:
                            intpropenv[temp[0]]=str(int(temp[1]))
                        except:
                            raise IndexError('did not enter a integer')
                    elif temp[0] in strpropenv:
                        strpropenv[temp[0]]=str(temp[1])
                    elif temp[0] in boolpropenv:
                        if (temp[1].lower() == "true" or temp[1].lower() == "false"):
                            boolpropenv[temp[0]]=(temp[1])
                        else:
                            raise IndexError('did not enter a valid boolean')
                    elif temp[0] in linkpropenv:
                        if temp[0] == 'DATAPACKS':
                            final = str(linkpropenv['DATAPACKS'])
                            linklst = temp[1].split('|')
                            lst = []
                            for link in linklst:
                                if (link=="add") or (link.lower()=="set"):
                                    continue
                                else:
                                    analysis = await cloudscript.virustest(link)
                                    if analysis == '1':
                                        lst.append(link)
                                    else:
                                        await ctx.send(analysis)
                                        return
                            if linklst[0].lower() == "add":
                                del linklst[0]
                                for old in linkpropenv['DATAPACKS'].split(','):
                                    lst.append(old)
                                lst = list(dict.fromkeys(lst)) # removes duplicates
                                linkpropenv['DATAPACKS'] = ",".join(lst)
                            if linklst[0].lower() == "set":
                                del linklst[0]
                                lst = list(dict.fromkeys(lst)) # removes duplicates
                                linkpropenv['DATAPACKS'] = ",".join(lst)
                        else:
                            analysis = await cloudscript.virustest(link)
                            if analysis == '1':
                                linkpropenv[temp[0]]=temp[1]
                            else:
                                await ctx.send(analysis)
                    elif temp[0] in otherpropenv:                      
                        linklst = temp[1].split('|')
                        if linklst[0].lower() == "add":
                            del linklst[0]
                            for link in linklst:
                                final = otherpropenv[temp[0]]
                                oldlst = final.split(",")
                                if link not in oldlst:
                                    final = final + str(link)
                                    final = final + ","
                                else:
                                    final = final + ","
                            if final[-1:] == ",":
                                final = final[:-1]
                        if linklst[0].lower() == "set":
                            del linklst[0]
                            final = ""
                            for link in linklst:
                                final = final + str(link)
                                final = final + ","
                            if final[-1:] == ",":
                                final = final[:-1]
                        otherpropenv[temp[0]]=final
                    elif temp[0] == 'MAX_MEMORY':
                        try:
                            if 2<int(temp[1])<8:
                                maxmemory[temp[0]]=str(temp[1]) + "G"
                            else:
                                raise OverflowError
                        except:
                            await ctx.send("Memory can only be between 2 and 8.")
                            return
                    else:
                        await ctx.send(f"Did not find {temp[0]} in valid environment variables. Please try again")
                        return
                except KeyboardInterrupt:
                        await ctx.send("Error reading values. Check your spelling and try again")
                        return

        #__setting the new environment variables as a new container while mounting the old volume__
            env = {**intpropenv, **strpropenv,**boolpropenv, **linkpropenv, **otherpropenv, **maxmemory, **self.defaultenv}
            portdict = self.db.search((where('serverId') == ctx.guild.id) & (where('name') == name))
            port = portdict[0]['port']
            replace = await podscript.replace(processname, env, port)
            await ctx.send(replace)
            self.db.update({'status': 'down'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
    @commands.command()
    async def delete(self, ctx: Context, name: str, keepworld = "False", worldname = None, * ,args = "A minecraft server"):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return  
        ids = self.db.search((where('serverId') == ctx.guild.id) & (where('name') == name))
        if len(ids) == 0:
            await ctx.send('Server does not exist.')
            return
        
        owner = self.db.get((where('serverId') == ctx.guild.id) & (where('name') == name))['owner']
        if str(ctx.author.id) not in botowners:
            if owner != ctx.author.id:
                await ctx.send("Only the minecraft server owner can do this")
                return   
        message = await ctx.send(f"Attempting to delete {name}")
        with PodmanClient(base_url=uri) as client:
            try:
                process=client.containers.get(name + "." + str(ctx.guild.id))
                process.stop()
            except:
                pass
            if keepworld.lower() == "true":
                if len(self.backups.search((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))):
                    await ctx.send("There is already a server with this name")
                    return
                if not worldname:
                    worldname = "unnamed world"
                envlst = process.inspect()['Config']['Env']
                envdict = {}
                for variables in envlst:             
                    templst = variables.split("=")
                    envdict[templst[0]] = templst[1]
                try: version = envdict['VERSION']
                except: version = "Latest"
                volumepath = process.inspect()['Mounts'][0]['Source']
               
                self.backups.insert({
                    'volume':
                    {
                        'name': volumepath.split("/")[volumepath.split("/").index('volumes') + 1], 
                        'Source': volumepath
                    }, 
                    'worldname': worldname, 
                    'type': ids[0]['type'],
                    'version': version,
                    'description': args,
                    'owner': owner, 
                    'guildId': ctx.guild.id
                })
                await ctx.send("Successfully saved the world")
                message = await ctx.send("Deleting the server...")
                process.remove()
            elif keepworld.lower() == "false":
                def check(m): 
                    return m.author == ctx.author and m.channel == ctx.channel
                try: 
                    await ctx.send("Are you sure you want to delete the world (There is no going back):\nTo confirm type (y)es. If no, type anything else")
                    response = await self.bot.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError: 
                    await response.edit("You did not confirm in time. Cancelling deletion")
                    self.db.update({'status': 'down'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
                    return
                if response.content.lower() not in ("yes", "y"):
                    message = await ctx.send("Cancelling deletion...")
                    self.db.update({'status': 'down'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
                    await message.edit(content = "Deletion has been cancelled")
                    return
                message = await ctx.send("Deleting the server...")
                try:
                    volumepath = process.inspect()['Mounts'][0]['Source']
                    volume = client.volumes.get(volumepath.split("/")[volumepath.split("/").index('volumes') + 1])
                    process.remove()
                    volume.remove()
                except Exception as e:
                    print (e)
            else:
                await ctx.send("Check your parameters for spelling errors")
                return
 
            try: await cloudscript.delete(name, ctx.guild.id)
            except Exception as e: print (e)
            self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
            await message.edit(content = f'Server with name "{name}" deleted.')
    @commands.command()
    async def transfer(self, ctx:Context, name: str, newowner: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        owner = self.db.get((where('serverId') == ctx.guild.id) & (where('name') == name))['owner']
        if owner != ctx.author.id:
            await ctx.send("Only the minecraft server owner can do this")
            return
        owner = newowner.replace("<","")
        owner = owner.replace(">","")
        owner = owner.replace("@","")
        owner = owner.replace("!","")
        owner = int(owner)
        querycheck = Query()
        maxperuser = self.conf.get(querycheck.guildId == ctx.guild.id)['maxperuser']
        maxservers = self.conf.get(querycheck.guildId == ctx.guild.id)['maxservers']
        maxworlds = self.conf.get(querycheck.guildId == ctx.guild.id)['maxworlds']
        currentactive = len(self.db.search((querycheck.owner == owner) & (querycheck.guildId == ctx.guild.id)))
        if currentactive>=maxperuser:
            if str(owner) not in botowners:
                await ctx.send(f"You can only have {maxperuser} servers active per person")
                return
        if len(self.backups.search((where('guildId') == ctx.guild.id) & (where('owner') == owner))) + currentactive >= maxworlds:
            if str(owner) not in botowners:
                await ctx.send(f"You can only have {maxperuser} servers active per person")
                return
        if len(self.db.search((querycheck.status == 'up') & (querycheck.guildId == ctx.guild.id)))>=maxservers:
            if str(owner) not in botowners:
                await ctx.send(f"This server can only have {maxservers} servers up at once")
                return
        def check(m): 
            return m.author == ctx.author and m.channel == ctx.channel
        try: 
            await ctx.send("Are you sure you want to transfer the world?\nTo confirm type (y)es. If no, type anything else")
            response = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError: return
        def check1(m): 
            return m.author.id == int(owner) and m.channel == ctx.channel
        try: 
            message = await ctx.send(f"Are you sure you want to accept the ownership? To confirm, have THEM type (y)es. If no, type anything else. \nCancelling in 30 seconds")
            response = await self.bot.wait_for('message', check=check1, timeout=30.0)
        except asyncio.TimeoutError: 
            await message.edit(content = f"<@{owner}> did not reply in time. Please try again")
            return
        if response.content.lower() not in ("yes", "y"):
            await ctx.send(f"<@{owner}> did not accept the transfer request.")
            return
        try: self.db.update({'owner': owner}, (where('serverId') == ctx.guild.id) & (where('name') == name))
        except: ctx.send("Something went wrong")
        await ctx.send("Transfer was successful")
        
    @commands.command()
    async def list(self, ctx: Context, type = all):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if type == "all":
            servers = [entry['name'] for entry in self.get(ctx)]
            if len(servers) == 0:
                await ctx.send('No servers')
                return
            status = [entry['status'] for entry in self.get(ctx)]
            for i in range(0,len(servers)-1):
                servers[i] = servers[i] + ": Status `" + status[i] + "`"
            await ctx.send('\n'.join(servers))
        elif type == "running" or "up" or "on":
            servers = [entry['name'] for entry in self.get(ctx)] 
            status = [entry['status'] for entry in self.get(ctx)]
            for i in range(0,len(servers)):
                servers[i] = servers[i] + ": Status `" + status[i] + "`"
            if len(servers) == 0:
                await ctx.send('No servers')
                return
            else:
                await ctx.send('\n'.join(servers))

    @commands.command()
    async def status(self,ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        processname = name + "." + str(ctx.guild.id)
        message = await podscript.status(processname)
        await ctx.send(f'The server is currently: `{message}`')
        return
    @commands.command()
    async def stop(self,ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        message = await ctx.send(f"Stopping the server '{name}'...")
        processname = name + "." + str(ctx.guild.id)
        stopping = await podscript.stop(processname)
        await message.edit(content = stopping)
        self.db.update({'status': 'down'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
    @commands.command()
    async def start(self,ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        processname = name + "." + str(ctx.guild.id)
        starting = await podscript.start(processname)
        await ctx.send(starting)
        finalip = await cloudscript.findip(name, ctx.guild.id)
        try: await asyncio.wait_for(self.startup(ctx, processname, finalip), timeout= 120)
        except asyncio.TimeoutError: pass
        self.db.update({'status': 'down'}, (where('serverId') == ctx.guild.id) & (where('name') == name))
    @commands.command()
    async def ip(self,ctx: Context, name: str):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        await ctx.send(f'The ip for "{name}" is:\n\n`{await cloudscript.findip(name, ctx.guild.id)}`')

    @commands.command()
    async def addplayer(self,ctx: Context, servername: str, whichlst: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.perms(ctx, servername):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, servername):
            await ctx.send('Server with this name does not exist.')
            return
        name = args.split(",")
        addplayers = await podscript.addplayers(whichlst,name,servername + "." + str(ctx.guild.id))
        if addplayers == 1:
            await ctx.send(f"Successfully added {args} to the {whichlst}")
        else:
            await ctx.send("Something went wrong. Check your parameters for spelling errors")
    @commands.command()
    async def removeplayer(self,ctx: Context, servername: str, whichlst: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        if not self.perms(ctx, servername):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        if not self.get(ctx, servername):
            await ctx.send('Server with this name does not exist.')
            return
        name = args.split(",")
        removeplayers = await podscript.removeplayers(whichlst,name,servername + "." + str(ctx.guild.id))
        if removeplayers == 1:
            await ctx.send(f"Successfully removed {args} from the {whichlst}")
        else:
            await ctx.send("Something went wrong. Check your parameters for spelling errors")
    @commands.command()
    async def addmoderator(self,ctx: Context, name: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        id: Guild.id = ctx.guild.id
        if not self.perms(ctx, name): 
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        lst = args.split()
        userlst = []
        for user in lst:
            user = user.replace("<","")
            user = user.replace(">","")
            user = user.replace("@","")
            user = user.replace("!","")
            userlst.append(str(user))
            await ctx.send(f"Added <@{user}> to list of moderators")
        for user in self.db.search((where('serverId') == id) & (where('name') == name))[0]['moderators']:
            userlst.append(user)
        
        userlst = list(set(userlst))

        self.db.update({'moderators': userlst}, (where('serverId') == id) & (where('name') == name))
    @commands.command()
    async def removemoderator(self,ctx: Context, name: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        id: Guild.id = ctx.guild.id
        if not self.perms(ctx, name):
            await ctx.send("Only the minecraft server owner and moderators can do this")
            return
        moderatorlist = self.db.search((where('serverId') == id) & (where('name') == name))[0]['moderators']
        lst = args.split()
        userlst = []
        for user in lst:
            user = user.replace("<","")
            user = user.replace(">","")
            user = user.replace("@","")
            user = user.replace("!","")
            userlst.append(str(user))
        for user in userlst:
            try: 
                userlst.remove(user)
                await ctx.send(f"Removed <@{user}> to list of moderators")
            except:
                await ctx.send(f"<@{user}> is not on the list of moderators")
        self.db.update({'moderators': userlst}, (where('serverId') == id) & (where('name') == name))
    @commands.command()
    async def restore(self, ctx: Context, worldname: str, *, args):
        if self.blacklisted(str(ctx.author.id)):
            await ctx.send('You were blacklisted by the bot owner')
            return
        querycheck = Query()
        maxperuser = self.conf.get(querycheck.guildId == ctx.guild.id)['maxperuser']
        maxservers = self.conf.get(querycheck.guildId == ctx.guild.id)['maxservers']
        if len(self.db.search((querycheck.owner == ctx.author.id) & (querycheck.guildId == ctx.guild.id)))>=maxperuser:
            if str(ctx.author.id) not in botowners:
                await ctx.send(f"You can only have {maxperuser} server per person")
                return
        if len(self.db.search((querycheck.status == 'up') & (querycheck.guildId == ctx.guild.id)))>=maxservers:
            if str(ctx.author.id) not in botowners:
                await ctx.send(f"This server can only have {maxservers} servers up at once")
                return
        oldworldinfo = self.backups.get((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
        if oldworldinfo:
            mounts = oldworldinfo['volume']['Source'] 
        else:
            await ctx.send(f"Cannot find old world named {worldname}")
            return
        arglist = str(args).split(",")
        newenv = {}
        name = None
        mountpoint = [{'type': 'bind', 'source': mounts, 'target': '/data'}]
        for a in arglist:
            temp = a.split("=")
            if temp[0].lower() == "version":
                newenv['VERSION'] = temp[1]
            elif temp[0].lower() == "name":
                if self.get(ctx, temp[1]):
                    await ctx.send('Server with name already exists.')
                    return
                name = temp[1]
            else:
                await ctx.send("Make sure you have the right required arguments")
                return
        mctype = oldworldinfo['type']
        if mctype.lower() == "custom":
            type = "VANILLA"
        else:
            type = mctype.upper()
        env = {**self.defaultenv, **newenv, 'TYPE': type}
        port = None
        for p in range (int(os.getenv('PORT_MIN')),int(os.getenv('PORT_MAX'))):
            portchecker = Query()
            if self.db.contains(portchecker.port == p):
                continue
            else:
                port = p
                break
        processname = str(name) + "." + str(ctx.guild.id)
        owner = ctx.author.id
        moderators = []
        mctype = oldworldinfo['type']
        self.db.insert({
        'serverId': ctx.guild.id,
        'name': name,
        'port': port,
        'type': mctype,
        'owner': owner,
        'moderators': moderators,
        'status': 'down'
        })

        
        await ctx.send(f'Server with name "{name}" on "{mctype}" added.')
        with PodmanClient(base_url=uri) as client:
            portnumber = {'25565': str(port)}
            client.containers.run('itzg/minecraft-server', environment=env, ports=portnumber, name=processname, mounts=mountpoint, detach=True) 
            finalip = await cloudscript.create(name, ctx.guild.id, port)
            self.backups.remove((where('guildId') == ctx.guild.id) & (where('owner') == ctx.author.id) & (where('worldname') == worldname))
            await self.startup(ctx,processname, finalip)


    @commands.command()
    async def test(self,ctx: Context, name: str, *, args):
        id: Guild.id = ctx.guild.id
        await ctx.send(self.db.search((where('serverId') == id) & (where('name') == name)))
        return
    @commands.command()
    async def info(self, ctx: Context, name: str):
        id = ctx.guild.id
        servername = name + "." + str(ctx.guild.id)
        owner = self.db.get((where('serverId') == id) & (where('name') == name))['owner']
        moderatorlst = []
        for moderators in self.db.get((where('serverId') == id) & (where('name') == name))['moderators']:
            moderatorlst.append("<@" + str(moderators) + ">")
        podmandict=await podscript.podinfo(servername)
        env = {}
        for variables in podmandict['Env']:             
            templst = variables.split("=")
            env[templst[0]] = templst[1]
        try: version = env['VERSION']
        except: version = "Latest"
        try: type = env['TYPE']
        except: type = "Vanilla"
        await ctx.send(f"""
The server "{name}" is a {type} server on version: {version}

Owner: <@{owner}> 
Moderators: {','.join(moderatorlst)}
*the server was created at {podmandict['Created'][:10]}*
        """)
    @commands.command()
    async def max(self, ctx: Context):
        querycheck = Query()
        maxperuser = self.conf.get(querycheck.guildId == ctx.guild.id)['maxperuser']
        maxworlds = self.conf.get(querycheck.guildId == ctx.guild.id)['maxworlds']
        maxservers = self.conf.get(querycheck.guildId == ctx.guild.id)['maxservers']
        await ctx.send(f"""The max is **{maxperuser} server(s)** per person and a total of **{maxworlds}** worlds
The server's max is **{maxservers} running minecraft servers** in each discord server: Please be considerate of other people.

You have **{len(self.db.search((querycheck.owner == ctx.author.id) & (querycheck.guildId == ctx.guild.id)))}** server(s)
There are **{len(self.db.search((querycheck.status == 'up') & (querycheck.guildId == ctx.guild.id)))}** servers up currently""")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing some required arguments")

        if isinstance(error, commands.CommandNotFound):
            await ctx.send("This is not a command. Check your spelling")
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def perms(self, ctx: Context, name: str):
        id: Guild.id = ctx.guild.id
        user = ctx.author.id
        for botowner in botowners:
            if botowner == str(user):
                return True
        if self.db.get((where('serverId') == id) & (where('name') == name))['owner'] == user:
            return True     
        for moderators in self.db.get((where('serverId') == id) & (where('name') == name))['moderators']:
            if moderators == user:
                return True
        return False

    def blacklisted(self, user: str):
        bannedlst = os.getenv('BOT_BLACKLISTED').split()
        for banned in bannedlst:
            if user == banned:
                return True
            else:
                return False
    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            return self.db.get((where('serverId') == id) & (where('name') == name))
        else:
            return self.db.search((where('serverId') == id))
    async def startup(self, ctx: Context, processname: str, finalip: str):
        with PodmanClient(base_url=uri) as client:
            message = await ctx.send ("Starting the Minecraft server...")
            process=client.containers.get(processname)
            is_starting=is_loading=is_finishing=True
            while is_starting:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode('utf-8').find("[init]") != -1:
                        await message.edit (content = "Started the Minecraft Server")
                        is_starting= False
                        break         
            while is_loading:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode('utf-8').find("Locating download") != -1:
                        await ctx.send("Preparing world...")
                        is_loading= False
                        break
            message = await ctx.send("Setting up the server")
            while is_finishing:
                await asyncio.sleep(1)
                for i in process.logs():
                    if i.decode('utf-8').find('For help') != -1:
                        is_finishing= False
                        break
                logs = list(process.logs(since=1))
                await message.edit(content = logs[-1].decode('utf-8'))
            await message.edit(content = f"The server is up on {finalip}")
            return