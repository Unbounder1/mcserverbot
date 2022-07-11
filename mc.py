from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from podman import PodmanClient
from dotenv import load_dotenv
from time import sleep
import nest_asyncio
import asyncio
nest_asyncio.apply()
import podscript
import cloudscript
import os
import vt
load_dotenv()

uri = os.getenv('URI')
CLIENT_TOKEN = os.getenv('VIRUSTOTAL_TOKEN')
class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)


    @commands.command()
    async def create(self, ctx: Context, name: str, mctype: str, *, args):
        if self.get(ctx, name):
            await ctx.send('Server with name already exists.')
            return
        
        mainenv = {'VERSION': None,'MAX_MEMORY': None}
        #__setting up the universal env variables__
        if len(args)>0 and args!="0":
            argslist = args.split(",")
            for a in argslist:
                temp = a.split("=")
                if temp[0] == "MAX_MEMORY":
                    try:
                        if 2<int(temp[1])<8:
                            mainenv[temp[0]]=str(temp[1]) + "G"
                        else:
                            raise OverflowError
                    except OverflowError:
                        await ctx.send("Memory can only be set between 2 and 8 gigabytes")
                        return
                elif temp[0] == 'VERSION':
                     mainenv[temp[0]]=temp[1]
        
        defaultenv = {
                    'GUI': "false", 
                    'EULA': "true", 
                    'INIT_MEMORY': "1G",

                    'OVERRIDE_SERVER_PROPERTIES' : "true", 
                    'REPLACE_ENV_IN_PLACE': "false",
                    'OVERRIDE_OPS': "false",
                    'OVERRIDE_WHITELIST': "false",
                    'REMOVE_OLD_DATAPACKS': 'true',
                    
                    #RCON
                    'ENABLE_RCON': "true",
                    'RCON_PASSWORD': "minecraft", #Advised to change this
                    #autopause stuff

                    'MAX_TICK_TIME' : "-1",
                    'ENABLE_AUTOPAUSE': "true",
                    'AUTOPAUSE_TIMEOUT_EST': "3600",
                    'AUTOPAUSE_KNOCK_INTERFACE' : "eno1",

                    #autostop stuff
                    'ENABLE_AUTOSTOP': "false",
                    'AUTOSTOP_TIMEOUT_EST': "172800" # 2 days
            }
        
        #__setting up the specific environmental variables__
        if mctype.lower() == "vanilla":
            env = {**defaultenv, **mainenv}
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
                        # with vt.Client(CLIENT_TOKEN) as client:
                        #     analysis = await client.scan_url_async(temp[1], wait_for_completion=True)
                        #     if analysis.stats['malicious'] > 0:
                        #         await ctx.send("Please contact bot owner to install")
                        #         return
                        #     elif analysis.stats['suspicious'] > 5:
                        #         await ctx.send("Please contact bot owner to install")
                        #         return 
                        #     else:
                        #         await ctx.send(analysis.stats)
                        #         return 

                        analysis  = await cloudscript.virustest(temp[1])
                        if analysis == '1':
                            linkpropenv[temp[0]]=temp[1]
                            await ctx.send("The links are somewhat valid")
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
                env = {**defaultenv, **mainenv, **linkpropenv, **otherpropenv, 'SEED': seed, 'TYPE': mctype.upper()}


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
        
        self.db.insert({
        'serverId': ctx.guild.id,
        'name': name,
        'port': port,
        'type': mctype
        })


        await ctx.send(f'Server with name "{name}" with added.')
        processname = name + "." + str(ctx.guild.id)

        #__starting the podman container__
        if podscript.create(processname, env, port)==0:
            await ctx.send("Something went wrong. Check your spelling and try again")
            self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
            return
        
        finalip = cloudscript.create(name, ctx.guild.id, port)

        #__sending server status messages__
        with PodmanClient(base_url=uri) as client:
                message = await ctx.send ("Starting the Minecraft server")
                process=client.containers.get(processname)
                is_starting=is_loading=is_finishing=True
                while is_starting:
                    sleep(1)
                    for i in process.logs(since=4):
                        if i.decode('utf-8').find("[init]") != -1:
                            await message.edit (content = "Started the Minecraft Server")
                            is_starting= False
                            break         
                while is_loading:
                    sleep(1)
                    for i in process.logs(since=4):
                        if i.decode('utf-8').find("INFO]") != -1:
                            await ctx.send("Preparing level")
                            is_loading= False
                            break
                message = await ctx.send("Setting up the server")
                while is_finishing:
                    sleep(1)
                    for i in process.logs(since=5):
                        if i.decode('utf-8').find('For help') != -1:
                            is_finishing= False
                            break
                    logs = list(process.logs(since=1))
                    await message.edit(content = logs[-1].decode('utf-8'))
                await message.edit(content = f"The server is up on {finalip}")
                return

    # @commands.command()
    # async def create(self, ctx: Context, help: str):
    #     await ctx.send("help thing")
    @commands.command()
    async def set(self, ctx: Context, name: str, *, args):
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
            
        message = await ctx.send("Attempting to set variables")
        #ADD CHECK FOR IF THE THING EXISTS OR NOT <-----------------------
        processname = name + "." + str(ctx.guild.id)
        defaultenv = {
            'GUI': "false", 
            'EULA': "true", 
            'INIT_MEMORY': "1G",

            'OVERRIDE_SERVER_PROPERTIES' : "true", 
            'REPLACE_ENV_IN_PLACE': "false",
            'OVERRIDE_OPS': "false",
            'OVERRIDE_WHITELIST': "false",
            'REMOVE_OLD_DATAPACKS': 'true',
            
            #RCON
            'ENABLE_RCON': "true",
            'RCON_PASSWORD': "minecraft", #Advised to change this
            #autopause stuff

            'MAX_TICK_TIME' : "-1",
            'ENABLE_AUTOPAUSE': "true",
            'AUTOPAUSE_TIMEOUT_EST': "3600",
            'AUTOPAUSE_KNOCK_INTERFACE' : "eno1",

            #autostop stuff
            'ENABLE_AUTOSTOP': "false",
            'AUTOSTOP_TIMEOUT_EST': "172800" # 2 days
    }

        intpropenv = strpropenv = specialpropenv = boolpropenv = {}
        intpropenv = dict.fromkeys(['TYPE','SPAWN_PROTECTION','VIEW_DISTANCE','MAX_BUILD_HEIGHT','MAX_WORLD_SIZE','MAX_PLAYERS'])
        strpropenv = dict.fromkeys(['OPS','SERVER_NAME','MOTD','DIFFICULTY'], None)
        boolpropenv = dict.fromkeys(['ENABLE_COMMAND_BLOCK','HARDCORE','WHITELIST'], None)
        linkpropenv = dict.fromkeys(['DATAPACKS','ICON'], None)
        otherpropenv = dict.fromkeys(['VANILLATWEAKS_SHARECODE','SPIGET_RESOURCES'], None)
        maxmemory = {'MAX_MEMORY': None}
        env = {'intpropenv':intpropenv,'strpropenv':strpropenv,'boolpropenv':boolpropenv,'linkpropenv':linkpropenv,'otherpropenv':otherpropenv, 'maxmemory': maxmemory}


        oldenvlst = podscript.findenv(processname)
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
                                print (linkpropenv['DATAPACKS'])
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
            env = {**intpropenv, **strpropenv,**boolpropenv, **linkpropenv, **otherpropenv, **maxmemory, **defaultenv}
            portdict = self.db.search((where('serverId') == ctx.guild.id) & (where('name') == name))
            port = portdict[0]['port']
            await ctx.send(podscript.replace(processname, env, port))

    @commands.command()
    async def delete(self, ctx: Context, name: str):        
        ids = self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
        if len(ids) == 0:
            await ctx.send('Server does not exist.')
            return
        await ctx.send(f'Server with name "{name}" deleted.')
        try: cloudscript.delete(name, ctx.guild.id)
        except: pass
        with PodmanClient(base_url=uri) as client:
            try:
                process=client.containers.get(name + "." + str(ctx.guild.id))
                process.stop()
                process.remove(v=True)
            except:
                pass


    @commands.command()
    async def list(self, ctx: Context):
        servers = [entry['name'] for entry in self.get(ctx)]
        if len(servers) == 0:
            await ctx.send('No servers')
            return
        await ctx.send('\n'.join(servers))
    @commands.command()
    async def status(self,ctx: Context, name: str):
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        processname = name + "." + str(ctx.guild.id)
        message = podscript.status(processname)
        await ctx.send(f'The server is currently: `{message}`')
        return
    @commands.command()
    async def stop(self,ctx: Context, name: str):
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        message = await ctx.send("Attempting to stop the server...")
        processname = name + "." + str(ctx.guild.id)
        await message.edit(content = podscript.stop(processname))

    @commands.command()
    async def start(self,ctx: Context, name: str):
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        processname = name + "." + str(ctx.guild.id)
        podscript.start(processname)
        with PodmanClient(base_url=uri) as client:
            message = await ctx.send ("Starting the Minecraft server...")
            process=client.containers.get(processname)
            is_starting=is_loading=is_finishing=True
            while is_starting:
                sleep(1)
                for i in process.logs(since=2):
                    if i.decode('utf-8').find("[init]") != -1:
                        await message.edit (content = "Started the Minecraft Server")
                        is_starting= False
                        break         
            while is_loading:
                sleep(1)
                for i in process.logs(since=2):
                    if i.decode('utf-8').find("[ServerMain/INFO]") != -1:
                        await ctx.send("Preparing world...")
                        is_loading= False
                        break
            message = await ctx.send("Setting up the server")
            while is_finishing:
                sleep(1)
                for i in process.logs(since=5):
                    if i.decode('utf-8').find('For help') != -1:
                        is_finishing= False
                        break
                logs = list(process.logs(since=1))
                await message.edit(content = logs[-1].decode('utf-8'))
            await message.edit(content = "The server is up!")
            return
    @commands.command()
    async def ip(self,ctx: Context, name: str):
        if not self.get(ctx, name):
            await ctx.send('Server with this name does not exist.')
            return
        await ctx.send(f'The ip for "{name}" is:\n\n`{cloudscript.findip(name, ctx.guild.id)}`')

    @commands.command()
    async def addplayer(self,ctx: Context, servername: str, whichlst: str, *, arg):
        if not self.get(ctx, servername):
            await ctx.send('Server with this name does not exist.')
            return
        name = arg.split(",")
        podscript.addplayers(whichlst,name,servername + "." + str(ctx.guild.id))

    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            return self.db.get((where('serverId') == id) & (where('name') == name))
        else:
            return self.db.search((where('serverId') == id))
