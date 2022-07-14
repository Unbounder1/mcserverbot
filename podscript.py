from dotenv import load_dotenv
import os
from discord.ext.commands import Context
from time import sleep
load_dotenv()
uri = os.getenv('URI')

from podman import PodmanClient

client = PodmanClient(base_url=uri)
async def findenv(name: str):
    with PodmanClient(base_url=uri) as client:
        oldenvlst=client.containers.get(name).inspect()["Config"]["Env"]
        return oldenvlst

async def create(name: str, env: dict, port: int, version = None):
    portnumber = {'25565': str(port)}
    imageversion = 'itzg/minecraft-server'
    if version:
        versionsplit = version.split(".")
        if (int(versionsplit[0]) == 1) & (int(versionsplit[1])<17):
            imageversion = 'itzg/minecraft-server:java8-multiarch'
            
    try:
        client.containers.run(imageversion, environment=env, ports=portnumber, name=name, detach=True)
        print("making container")
    except Exception as e:
        print (e)
        try:
            process=client.containers.get(name)
            try: process.stop()
            
            finally:
                try: 
                    volume = client.volumes.get(process.inspect()['Mounts'][0]['Name'])
                    process.remove()
                    volume.remove()

                finally: return 0
        finally: return 0
    return 1

async def replace(name: str, env: dict, port: int):
    portnumber = {'25565': str(port)}
    process=client.containers.get(name)
    mountpoint = [{'type': 'bind', 'source': process.inspect()["Mounts"][0]["Source"], 'target': '/data'}]
    try: process.stop()
    except: pass
    tempname = name + "temp"
   
    try: 
        process.rename(tempname)
        try: 
            client.containers.run('itzg/minecraft-server', environment=env, name=name , mounts=mountpoint, detach=True, auto_remove=True) 
            process=client.containers.get(name)
            process.remove(force=True)
        except:
            return "Check your spelling"
        process=client.containers.get(tempname)
        process.remove()
        client.containers.run('itzg/minecraft-server', environment=env, ports=portnumber, name=name, mounts=mountpoint, detach=True) 
        process=client.containers.get(name)
        process.stop()
        return "Sucessfully set new variables"
    except:
        try: 
            client.containers.get(tempname).stop()
            client.containers.get(name).stop()
        finally:
            process=client.containers.get(tempname)
            process.rename(name)
        return "Are you sure your parameters are right?"
async def status(name: str):
    try: process=client.containers.get(name)
    except:
        return ("Does not exist")
    return str(process.status)
async def stop(name: str):
    process=client.containers.get(name)
    try: 
        process.stop()
        return "The server has been stopped"
    except: return "The server has already been stopped."
async def start(name: str):
    process=client.containers.get(name)
    try:
        process.start()
        return "The start command has executed"
    except:
        return "The server is already on"
async def addplayers(whichlst: str, name: list, processname: str):
    if whichlst.lower() == 'whitelist':
        for user in name:
            command = "podman-remote exec " + processname + " rcon-cli " + "whitelist add" + user + " >/dev/null 2>&1"
        return 1
    elif whichlst.lower() == 'ops':
        for user in name:
            command = "podman-remote exec " + processname + " rcon-cli " + "op " + user + " >/dev/null 2>&1"
            os.system(command)
        return 1
    else:
        return 0
async def removeplayers(whichlst: str, name: list, processname: str):
    if whichlst.lower() == 'whitelist':
        for user in name:
            command = "podman-remote exec " + processname + " rcon-cli " + "whitelist remove" + user + " >/dev/null 2>&1"
        return 1
    elif whichlst.lower() == 'ops':
        for user in name:
            command = "podman-remote exec " + processname + " rcon-cli " + "deop " + user + " >/dev/null 2>&1"
            os.system(command)
        return 1
    else:
        return 0
async def podinfo(name: str):
    oldenvlst=client.containers.get(name).inspect()
    returndict = {'Env': oldenvlst['Config']['Env'], 'Created': oldenvlst['Created']}
    return returndict