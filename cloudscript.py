import CloudFlare
import os
from tinydb import TinyDB, where, Query
from tinydb import where
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('CLOUDFLARE_TOKEN')
domain = os.getenv('DOMAIN')
ip = os.getenv('PUBLIC_IP')
cf = CloudFlare.CloudFlare(token=token)

def create(inputname: str, guildid: int, port: int):
    query = Query()
    db = TinyDB('domainnameDB.json')
    prefix = db.search(query['guildId'] == guildid)[0]['domainprefix']
    name = prefix + "-" + inputname
    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']

    cf.zones.dns_records.post(zone_id, data={'type': 'A', 'name':name, 'content':ip, 'proxied': True})
    cf.zones.dns_records.post(zone_id, data={'type': 'SRV', 'data': {'service': '_minecraft', 'proto': '_tcp', 'name':name, 'priority': 1, 'weight': 1, 'port': port, 'target':name + '.voark.com'}})
    return name + "." + domain
def delete(inputname: str, guildid: int):
    query = Query()
    db = TinyDB('domainnameDB.json')
    prefix = db.search(query['guildId'] == guildid)[0]['domainprefix']
    name = prefix + "-" + inputname
    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']

    dns_id=cf.zones.dns_records.get(zone_id, params={'type': 'SRV', 'name': '_minecraft._tcp.' + name + "." + domain})[0]['id']
    cf.zones.dns_records.delete(zone_id, dns_id)

    zone = cf.zones.get(params={'name': domain})
    zone_id = zone[0]['id']
    dns_id=cf.zones.dns_records.get(zone_id, params={'type': 'A', 'name':name})[0]['id']

    cf.zones.dns_records.delete(zone_id, dns_id)
    return
def findip(inputname: str, guildid: int):
    query = Query()
    db = TinyDB('domainnameDB.json')
    prefix = db.search(query['guildId'] == guildid)[0]['domainprefix']
    name = prefix + "-" + inputname + "." + domain
    return name

