from http.client import NOT_FOUND
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from podman import PodmanClient
from dotenv import load_dotenv
from time import sleep
import podscript
import os
load_dotenv()

uri = os.getenv('URI')
class MC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB('serverDB.json').table(name='_default', cache_size = 0)


    @commands.command()
    async def create(self, ctx: Context, name: str, mctype: str, *, args):
        if self.get(ctx, name):
            await ctx.send('Server with name already exists.')
            return
            
        #__checking arguments__
        mainenv = {'VERSION': None,'MAX_MEMORY': None}
        if len(args)>0 and args!="0":
            arglist = args.split()
            for a in arglist:
                temp = a.split("=")
                if temp[0] in mainenv:
                    mainenv[temp[0]]=temp[1]
                else:
                    await ctx.send("Please check your spelling for " + temp[0])
                    return

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
                'AUTOPAUSE_KNOCK_INTERFACE' : "eno1",

                #autostop stuff
                'ENABLE_AUTOSTOP': "false",
                'AUTOSTOP_TIMEOUT_EST': "172800" # 2 days

        }
        env = {**defaultenv, **mainenv}
        #add modpack stuff later --------------------------
        self.db.insert({
           'serverId': ctx.guild.id,
           'name': name,
           'port': "",
           'ready': False
        })

        await ctx.send(f'Server with name "{name}" with added.')
        processname = name + "." + str(ctx.guild.id)
        port = 25565 #    TEMP TEMPTEMP TMEPMPTMEPMTPEMTMEPPMETMPEMPEMTPEMPT TEMPORARY
        #__starting the podman container__
        if podscript.create(processname, env, port)==0:
            await ctx.send("Something went wrong. Check your spelling and try again")
        with PodmanClient(base_url=uri) as client:
                message = await ctx.send ("Starting the Minecraft server")
                process=client.containers.get(processname)
                is_starting=is_loading=is_finishing=True
                while is_starting:
                    sleep(1)
                    for i in process.logs(since=2):
                        if i.decode('utf-8').find("Unpacking") != -1:
                            await message.edit (content = "Started the Minecraft Server")
                            is_starting= False
                            break         
                while is_loading:
                    sleep(1)
                    for i in process.logs(since=2):
                        if i.decode('utf-8').find("[ServerMain/INFO]") != -1:
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
                await message.edit(content = "The server is up!")

    @commands.command()
    async def set(self, ctx: Context, name: str, *, args):
        #ADD CHECK FOR IF THE THING EXISTS OR NOT <-----------------------
        processname = name + "." + str(ctx.guild.id)
        intpropenv = strpropenv = specialpropenv = boolpropenv = {}
        intpropenv = dict.fromkeys(['SEED','SPAWN_PROTECTION','VIEW_DISTANCE','MAX_BUILD_HEIGHT','MAX_WORLD_SIZE','MAX_PLAYERS'])
        strpropenv = dict.fromkeys(['OPS','SERVER_NAME','MOTD','DIFFICULTY','WORLD','MAX_MEMORY'], None)
        boolpropenv = dict.fromkeys(['ENABLE_COMMAND_BLOCK','HARDCORE','WHITELIST'], None)
        specialpropenv = dict.fromkeys(['VANILLATWEAKS_SHARECODE','DATAPACKS','SPIGET_RESOURCES','ICON',], None)
        env = {'intpropenv':intpropenv,'strpropenv':strpropenv,'boolpropenv':boolpropenv,'specialpropenv':specialpropenv}


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
            arglist = args.split()
            for a in arglist:
                try:
                    temp = a.split('=')
                    if temp[0] in env['intpropenv']:           
                        try:
                            intpropenv[temp[0]]=str(int(temp[1]))
                        except:
                            raise IndexError('did not enter a integer')
                    elif temp[0] in env['strpropenv']:
                        strpropenv[temp[0]]=str(temp[1])
                    elif temp[0] in env['boolpropenv']:
                        if (temp[1].lower() == "true" or temp[1].lower() == "false"):
                            boolpropenv[temp[0]]=(temp[1])
                        else:
                            raise IndexError('did not enter a valid boolean')
                    else:
                        await ctx.send(f"Did not find {temp[0]} in valid environment variables. Please try again")
                        return
                except:
                        await ctx.send("Error reading values. Check your spelling and try again")
                        return

        #__setting the new environment variables as a new container while mounting the old volume__
            env = {**intpropenv, **strpropenv, **specialpropenv,**boolpropenv}
            await ctx.send(podscript.replace(processname, env, port="25565"))

    @commands.command()
    async def delete(self, ctx: Context, name: str):
        ids = self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
        if len(ids) == 0:
            await ctx.send('Server does not exist.')
            return
        await ctx.send(f'Server with name "{name}" deleted.')
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

    def get(self, ctx: Context, name: str = None):
        id: Guild.id = ctx.guild.id
        if name:
            return self.db.get((where('serverId') == id) & (where('name') == name))
        else:
            return self.db.search((where('serverId') == id))

