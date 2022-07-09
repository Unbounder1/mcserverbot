import json
from dotenv import load_dotenv
import os
from discord.ext.commands import Context
from time import sleep
load_dotenv()
uri = os.getenv('URI')

from podman import PodmanClient
client = PodmanClient(base_url=uri)
def findenv(name: str):
    oldenvlst=client.containers.get(name).inspect()["Config"]["Env"]
    return oldenvlst

def create(name: str, env: dict, port: int):
    portnumber = {str(port): '25565'}
    client.containers.run('itzg/minecraft-server', environment=env, ports=portnumber, name=name, detach=True)
    try:
        #client.containers.run('itzg/minecraft-server', environment=env, ports=port, name=name, detach=True)
        print("making container")
    except:
        try:
            process=client.containers.get(name)
            try: process.stop()
            
            finally:
                try: process.remove(v=True, force=True)

                finally: return 0
        finally: return 0
    return 1

def replace(name: str, env: dict, port: str):
    portnumber = {port: '25565'}
    process=client.containers.get(name)
    mountpoint = [{'type': 'bind', 'source': process.inspect()["Mounts"][0]["Source"], 'target': '/data'}]
    process.stop()
    tempname = name + "temp"
   
    try: 
        #unusedport = {'25555':'25565'} #set first part to a port that will never be used
        process.rename(tempname)
        client.containers.run('itzg/minecraft-server', environment=env, ports=portnumber, name=name , mounts=mountpoint, detach=True) 
        process=client.containers.get(tempname)
        process.remove()
        return "Sucessfully set new variables"
    except:
        try: 
            client.containers.get(tempname).stop()
            client.containers.get(name).stop()
        except:
            process=client.containers.get(tempname)
            process.rename(name)
            process.start()
        return "Are you sure your parameters are right?"

        # try:
        #     process.remove()
            
        #     return "Server set successfully"
        # except:
        #     process=client.containers.get(tempname)
        #     process.stop()
        #     return "Something went wrong. Please try again"

async def status(ctx: Context, processname):
    message = await ctx.send ("Starting the Minecraft server")
    with PodmanClient(base_url=uri) as client:
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
                logs = list(process.logs(since=1))
                await message.edit(content = logs[-1].decode('utf-8'))
                if i.decode('utf-8').find('For help, type "help"') != -1:
                    await message.edit(content = "The server is up!")
                    is_finishing= False
                    break
        return