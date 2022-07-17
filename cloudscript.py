import asyncio
import nest_asyncio
nest_asyncio.apply()
import CloudFlare
import os
from tinydb import TinyDB, where, Query
from tinydb import where
from dotenv import load_dotenv
import vt
load_dotenv()
token = os.getenv('CLOUDFLARE_TOKEN')
domain = os.getenv('DOMAIN')
ip = os.getenv('PUBLIC_IP')
CLIENT_TOKEN = os.getenv('VIRUSTOTAL_TOKEN')

cf = CloudFlare.CloudFlare(token=token)

async def create(inputname: str, guildid: int, port: int):
    query = Query()
    db = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)
    prefix = db.get(query['guildId'] == guildid)['domainprefix']
    if (prefix == "main"):
        name = inputname
    else:
        name = inputname + "-" + prefix
    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']

    cf.zones.dns_records.post(zone_id, data={'type': 'A', 'name':name, 'content':ip, 'proxied': True})
    cf.zones.dns_records.post(zone_id, data={'type': 'SRV', 'data': {'service': '_minecraft', 'proto': '_tcp', 'name':name, 'priority': 1, 'weight': 1, 'port': port, 'target':name + '.voark.com'}})
    return name + "." + domain
async def delete(inputname: str, guildid: int):
    query = Query()
    db = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)
    prefix = db.get(query['guildId'] == guildid)['domainprefix']
    if (prefix == "main"):
        name = inputname
    else:
        name = inputname + "-" + prefix
    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']

    dns_id=cf.zones.dns_records.get(zone_id, params={'type': 'SRV', 'name': '_minecraft._tcp.' + name + "." + domain})[0]['id']
    cf.zones.dns_records.delete(zone_id, dns_id)

    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']
    dns_id=cf.zones.dns_records.get(zone_id, params={'type': 'A', 'name':name + "." + domain})[0]['id']

    cf.zones.dns_records.delete(zone_id, dns_id)
    return
async def findip(inputname: str, guildid: int):
    query = Query()
    db = TinyDB('serverDB.json').table(name='_serverconf', cache_size = 0)
    prefix = db.get(query['guildId'] == guildid)['domainprefix']
    if (prefix == "main"):
        name = inputname + "." + domain
    else:
        name = inputname + "-" + prefix + "." + domain
    return name
async def virustest(url: str):
    async with vt.Client(CLIENT_TOKEN) as client:
        analysis = await client.scan_url_async(url, wait_for_completion=True)
        if analysis.stats['malicious'] > 0:
            return "Please contact bot owner to install"
        elif analysis.stats['suspicious'] > 5:
            return "Please contact bot owner to install"
        else:
            return '1'
        return "The link does not seem to be valid or something went wrong"