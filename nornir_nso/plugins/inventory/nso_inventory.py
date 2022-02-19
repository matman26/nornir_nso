from nornir.core.inventory import Inventory
from nornir.core.inventory import Defaults
from nornir.core.inventory import Groups
from nornir.core.inventory import Hosts
from nornir.core.inventory import Host
from typing import Dict
from typing import Any
import requests
import json

DEVICES_ENDPOINT = "restconf/data/tailf-ncs:devices/device/"

def platform_convert(platform: str):
    p_mapping = {
        "ios"    : "cisco_ios",
        "ios-xr" : "cisco_xr",
        "ios-xe" : "cisco_xe",
        "NX-OS"  : "cisco_nxos",
        "asa"    : "cisco_asa",
    }
    return p_mapping.get(platform, "")

def lookup_user_pass(authgroup: str):
    return 'cisco', 'cisco'

class NsoInventory:
    def __init__(self,
                 nso_url : str,
                 nso_username : str,
                 nso_password : str,
                 port : int = 443,
                 protocol : str = 'https',
                 verify : bool = True,
                 **kwargs
                 ):
        self.endpoint = nso_url
        self.username = nso_username
        self.password = nso_password
        self.protocol = protocol
        self.port     = port
        self.verify   = verify
        self.kwargs   = kwargs

    def get_devices(self) -> Dict[Any,Any]:
        result =  requests.get(
            f"{self.protocol}://{self.endpoint}:{str(self.port)}/{DEVICES_ENDPOINT}",
            auth=(self.username, self.password),
            headers={"Accept": 'application/yang-data+json', "Content-Type": 'application/yang-data+json'},
            verify=self.verify,
            **self.kwargs
        )

        return json.loads(result.text)

    def load(self) -> Inventory:
        nso_hosts = self.get_devices()
        hosts = Hosts()
        for device in nso_hosts['tailf-ncs:device']:
            username, password = lookup_user_pass(device['authgroup'])
            hosts[device['name']] = Host(
                name=device['name'],
                hostname=device['address'],
                platform=platform_convert(device['platform']['name']),
                username=username,
                password=password,)
        return Inventory(hosts=hosts,groups=Groups(),defaults=Defaults())

if __name__ == "__main__":
    endpoint = "10.10.20.49"
    username = "developer"
    password = "C1sco12345"
    nso = NsoInventory(endpoint,username,password,443,protocol='https',verify=False,timeout=30)
    inv = nso.load()
