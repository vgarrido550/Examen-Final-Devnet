from ncclient import manager

router = {
    'host': '192.168.56.102',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False
}

netconf_config = """
<config>
    <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <hostname>Victor-Garrido</hostname>
    </native>
</config>
"""

with manager.connect(**router) as m:
    respuesta = m.edit_config(target="running", config=netconf_config)

    print("Hostname cambiado correctamente")
    print(respuesta)