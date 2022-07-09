from dotenv import load_dotenv
import os
from discord.ext.commands import Context
from time import sleep
load_dotenv()
uri = os.getenv('URI')

from podman import PodmanClient

client = PodmanClient(base_url=uri)
def findenv(name: str):
    with PodmanClient(base_url=uri) as client:
        oldenvlst=client.containers.get(name).inspect()["Config"]["Env"]
        return oldenvlst

def create(name: str, env: dict, port: int):
    portnumber = {str(port): '25565'}
    with PodmanClient(base_url=uri) as client:
        try:
            client.containers.run('itzg/minecraft-server', environment=env, ports=portnumber, name=name, detach=True)
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

def replace(name: str, env: dict, port: int):
    portnumber = {str(port): '25565'}
    process=client.containers.get(name)
    mountpoint = [{'type': 'bind', 'source': process.inspect()["Mounts"][0]["Source"], 'target': '/data'}]
    process.stop()
    tempname = name + "temp"
   
    try: 
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
def status(name: str):
    process=client.containers.get(name)
    return str(process.status)
def stop(name: str):
    process=client.containers.get(name)
    try: 
        process.stop()
        return "The container has been stopped"
    except: return "The container has already been stopped."
def start(name: str):
    process=client.containers.get(name)
    try:
        process.start()
        return "The container has been started"
    except:
        return "The container is already on"
# async def creationstatus(ctx: Context, processname):
#     message = await ctx.send ("Starting the Minecraft server")
#     with PodmanClient(base_url=uri) as client:
#         process=client.containers.get(processname)
#         is_starting=is_loading=is_finishing=True
#         while is_starting:
#             sleep(1)
#             for i in process.logs(since=2):
#                 if i.decode('utf-8').find("Unpacking") != -1:
#                     await message.edit (content = "Started the Minecraft Server")
#                     is_starting= False
#                     break
                
#         while is_loading:
#             sleep(1)
#             for i in process.logs(since=2):
#                 if i.decode('utf-8').find("[ServerMain/INFO]") != -1:
#                     await ctx.send("Preparing level")
#                     is_loading= False
#                     break
#         message = await ctx.send("Setting up the server")
#         while is_finishing:
#             sleep(1)
#             for i in process.logs(since=5):
#                 logs = list(process.logs(since=1))
#                 await message.edit(content = logs[-1].decode('utf-8'))
#                 if i.decode('utf-8').find('For help, type "help"') != -1:
#                     await message.edit(content = "The server is up!")
#                     is_finishing= False
#                     break
#         return