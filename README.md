# nornir_nso
Nornir Plugin for interacting with Cisco's NSO.

## NsoInventory
NsoInventory is an inventory plugin for reading Nornir hosts from
NSO's CDB. Devices are collected from `restconf/data/tailf-ncs:devices/device`
so RESTCONF must be enabled on the NSO instance.

A sample nornir config file looks like the following:

```yaml
---
inventory:
  plugin: NsoInventory
  options:
    nso_hostname: sandbox-nso-1.cisco.com
    nso_username: developer
    nso_password: Services4Ever
    protocol: https  # optional, default https
    verify: True  # optional, default True
    port: 443  # optional, default 443
    # extra keyword arguments are passed directly to the requests.get() call
runner:
  plugin: threaded
  options:
    num_workers: 20
```

Notice that NSO does not supply authentication information (device passwords)
in plain-text via API, so they must be supplied for each authgroup. To supply credentials
for the authgroups present in your NSO instance, write an `authgroups.yaml` file
at the your working directory with the following structure:

```yaml
---
authgroup:
  labadmin:
    remote-name: cisco
    remote-password: cisco
  ...
  <your-authgroup-name>:
    remote-name: <your-authgroup-username>
    remote-password: <your-authgroup-password>
```

Remember to register the inventory plugin before usage.
```python
from nornir_nso.plugins.inventory.nso_inventory import NsoInventory
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir import InitNornir

InventoryPluginRegister.register("NsoInventory", NsoInventory)

nr = InitNornir(config_file="config.yaml")

# Do your stuff here...
```
