from nornir.core.inventory import Inventory
from nornir.core.inventory import Defaults
from nornir.core.inventory import Groups
from nornir.core.inventory import Hosts
from nornir.core.inventory import Host
from typing import Tuple
from typing import Dict
from typing import Any
import ruamel.yaml
import requests
import logging
import json

logger = logging.getLogger(__name__)

DEVICES_ENDPOINT = "restconf/data/tailf-ncs:devices/device/"

def platform_convert(platform: str) -> str:
    p_mapping = {
        "ios"    : "cisco_ios",
        "ios-xr" : "cisco_xr",
        "ios-xe" : "cisco_xe",
        "NX-OS"  : "cisco_nxos",
        "asa"    : "cisco_asa",
    }
    return p_mapping.get(platform, "")

def load_yaml(source_file: str) -> Dict[str, Any]:
    yml = ruamel.yaml.YAML(typ="safe")
    with open(source_file,'r') as f:
        data = yml.load(f) or {}
    return data

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
        self.endpoint   = nso_url
        self.username   = nso_username
        self.password   = nso_password
        self.protocol   = protocol
        self.port       = port
        self.verify     = verify
        self.kwargs     = kwargs
        self.authgroups = load_yaml('authgroups.yaml')

    def lookup_user_pass(self, authgroup: str) -> Tuple[str, str]:
        try:
            username = self.authgroups['authgroup'][authgroup]['remote-name']
            password = self.authgroups['authgroup'][authgroup]['remote-password']
        except KeyError:
            logger.critical(f"Could not find Authgroup credentials for authgroup {authgroup}.")
            logger.critical("Verify your auth.yaml file.")
            raise Exception("AuthGroupLookUpFailure")
        return username, password

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
            username, password = self.lookup_user_pass(device['authgroup'])
            hosts[device['name']] = Host(
                name=device['name'],
                hostname=device['address'],
                platform=platform_convert(device['platform']['name']),
                username=username,
                password=password,)
        return Inventory(hosts=hosts,groups=Groups(),defaults=Defaults())
