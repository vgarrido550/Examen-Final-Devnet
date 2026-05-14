from ncclient import manager

router = {
    'host': '192.168.56.102',
    'port': 830,
    'username': 'cisco',
    'password': 'cisco',
    'hostkey_verify': False
}

loopback_config = """
<config>
<native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
    <interface>
        <Loopback>
            <name>11</name>
            <description>Loopback NETCONF</description>
            <ip>
                <address>
                    <primary>
                        <address>11.11.11.11</address>
                        <mask>255.255.255.255</mask>
                    </primary>
                </address>
            </ip>
        </Loopback>
    </interface>
</native>
</config>
"""

with manager.connect(**router) as m:
    respuesta = m.edit_config(target="running", config=loopback_config)

    print("Loopback 11 creada correctamente")
    print(respuesta)