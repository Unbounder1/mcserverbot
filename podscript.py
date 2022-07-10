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
    portnumber = {'25565': str(port)}
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
def status(name: str):
    try: process=client.containers.get(name)
    except:
        return ("Does not exist")
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