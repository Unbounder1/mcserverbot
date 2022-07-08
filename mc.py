from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context
from tinydb import TinyDB, Query, where
from podman import PodmanClient
from dotenv import load_dotenv
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
        if len(args)>0:
            arglist = args.split()
            for a in arglist:
                temp = a.split("=")
                if temp[0] in mainenv:
                    mainenv[temp[0]]=temp[1]
                else:
                    await ctx.send("Please check your spelling for " + temp[0])
                    return
        

        #mandatory things
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
        await ctx.send(f'Server with name "{name}" with added.')

        #__starting the podman container__
        with PodmanClient(base_url=uri) as client:
            
            try:
                servername = name + "." + str(ctx.guild.id)
                client.containers.run('itzg/minecraft-server', environment=env, ports={'25566':'25565'}, name=servername, detach=True)
                
            except:
                try:
                    process=client.containers.get(servername)
                    process.stop()
                    process.remove()
                finally:
                    await ctx.send("Something went wrong. Try again.")
                    return
            process=client.containers.get(servername)
            is_starting = True
            is_loading = True
            is_finished = True

            while is_starting:
                for i in process.logs():
                    if i.decode('utf-8').find("Starting the Minecraft server") != -1:
                        await ctx.send ("Starting the Minecraft server")
                        is_starting= False
            # while is_loading:
            #     for i in process.logs():
            #         if i.decode('utf-8').find("Preparing level") != -1:
            #             message = await ctx.send ("Preparing level")
            #             await message.edit(i.decode('utf-8'))
            #             is_loading= False
            #------------------ gonna figure ^ out later want it to edit message with the loading percentage
            while is_finished:
                for i in process.logs():
                    if i.decode('utf-8').find("Time elapsed") != -1:
                        await ctx.send ("The server is up!")
                        is_finished= False

    @commands.command()
    async def set(self, ctx: Context, name: str, *, args):
        #ADD CHECK FOR IF THE THING EXISTS OR NOT <-----------------------

        intpropenv = strpropenv = specialpropenv = boolpropenv = {}
        intpropenv = dict.fromkeys(['SEED','SPAWN_PROTECTION','VIEW_DISTANCE','MAX_BUILD_HEIGHT','MAX_WORLD_SIZE','MAX_PLAYERS'])
        strpropenv = dict.fromkeys(['OPS','SERVER_NAME','MOTD','DIFFICULTY','WORLD',], None)
        boolpropenv = dict.fromkeys(['ENABLE_COMMAND_BLOCK','HARDCORE','WHITELIST'], None)
        specialpropenv = dict.fromkeys(['VANILLATWEAKS_SHARECODE','DATAPACKS','SPIGET_RESOURCES','ICON',], None)
        env = {'intpropenv':intpropenv,'strpropenv':strpropenv,'boolpropenv':boolpropenv,'specialpropenv':specialpropenv}


        with PodmanClient(base_url=uri) as client:
            processname = name + "." + str(ctx.guild.id)
            process=client.containers.get(processname)
            oldenvlst=process.inspect()["Config"]["Env"]
            oldenvdict = {}

            #__converting the list output of 'podman inspect' to a dictionary format__
            for variables in oldenvlst:             
                i=0
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
                        intpropenv[temp[0]]=int(temp[1])
                        # try:
                        #     intpropenv[temp[0]]=int(temp[1])
                        # finally:
                        #     raise IndexError('did not enter a integer')
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
            with PodmanClient(base_url=uri) as client:
                processname = name + "." + str(ctx.guild.id)
                try:
                    env = {**intpropenv, **strpropenv, **boolpropenv, **specialpropenv}
                    mountpoint = [{'type': 'bind', 'source': process.inspect()["Mounts"][0]["Source"], 'target': '/data'}]
                    try:
                        client.containers.get(processname).stop()
                    finally:
                        client.containers.get(processname).remove()
                        client.containers.run('itzg/minecraft-server', environment=env, ports={'25565':'25565'}, name=processname, mounts=mountpoint, detach=True)    

                except:
                    await ctx.send("Failed to start. Check your parameters and try again")
                    try:
                        process=client.containers.get(processname)
                        process.stop()
                        process.remove()
                    finally:
                        return

    @commands.command()
    async def delete(self, ctx: Context, name: str):
        ids = self.db.remove((where('serverId') == ctx.guild.id) & (where('name') == name))
        if len(ids) == 0:
            await ctx.send('Server does not exist.')
            return
        await ctx.send(f'Server with name "{name}" deleted.')
        with PodmanClient(base_url=uri) as client:
            process=client.containers.get(name + "." + str(ctx.guild.id))
            process.stop()
            process.remove()



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
