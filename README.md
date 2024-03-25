# Switch Connector

A python server which provides an Abstraction layer for interacting with Cisco switches.

## Technical challenge

Configuring network appliances requires knowledge about it's cli syntax and semanthics. Every device also has different protocol to interact (ssh, restconf, gnmi and so on)

# Proposed solution
Design and develop a mediator which abstract model specific syntax, allowing a user to be agnostic of OS and required CLI command to perform various operation.
Hiding the protocol being used to configure the device (ssh or restconf) and output a standardized message is a unique challenge.




# Technologies, tools and libraries used
- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [Genie Parser](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/?ref=packetswitch.co.uk#/parsers)
- [Scrapli](https://github.com/scrapli/scrapli_community)
- [Cisco Interface Name Converter](https://github.com/TimothyHarder/CiscoInterfaceNameConverter)


# Install and run

Requirements: [Python](https://www.python.org/) , [Pip](https://pip.pypa.io/en/stable/installation/)

open cmd:

    git clone https://github.com/giacomotontini/SwitchConnector-DevNet.git
    cd SwitchConnector-DevNet
    
    python -m venv sc-venv
    source ./sc-venv/bin/activate

    pip install -r requirements.txt

    python -m swagger_server

# How to use

We recommend using Postman to try and interact with this solution. In this readme we'll include cURL examples which is also fine

### Device Inventory
First thing first we need to provide a device inventory; a list of devices info that Switch Connector needs in order to interact and configure devices.
Prepare and POST a JSON to http://localhost:8080/inventory
```
curl --location 'http://localhost:8080/inventory' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '[
    {
        "ip": "192.168.0.10",
        "username": "admin",
        "password": "your_switch_password"
    },
    {
        "ip": "192.168.0.20",
        "username": "admin",
        "password": "your_switch_password"
    }]'
```

## Other endpoints 
### Gathering hardware info from a target device
Query parameters: ip (ip of the devices to be queried)
```
curl --location 'http://localhost:8080/switch/hardware/info?ip=192.168.0.10'
```
Expected output 
```
{
    "chassis": "C9200L-24P-4G",
    "chassis_sn": "XXXXXXXXXXX",
    "hostname": "C9200-1",
    "image_id": "CAT9K_LITE_IOSXE",
    "management_protocol": "RESTCONF",
    "platform": "Catalyst L3 Switch",
    "version": "17.6.4"
}
```

### Gathering vlan list of vlan db from a target device
Query parameters: ip (ip of the devices to be queried)
```
curl --location 'http://localhost:8080/switch/vlan?ip=192.168.0.10' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json'
```
Expected output 
```
[
    {
        "id": 1,
        "name": "default"
    },
    {
        "id": 12,
        "name": "MGMT"
    },
    {
        "id": 401,
        "name": "TEST401"
    },
    {
        "id": 402,
        "name": "TEST402"
    },
    {
        "id": 500,
        "name": "RSPAN"
    }
]
```
### Gathering switchport mode of a specific interface on a target device
Query parameters: ip (ip of the devices to be queried)
Route parameters: interface to gather info
```
curl --location --request GET 'http://localhost:8080/switch/interfaces/Gi1%2F0%2F23/switchport-conf?ip=192.168.0.10' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json'
```
Note that Gi1/0/23 is passed as a route parameer and MUST be URL encoded
Expected output 
```
{
    "mode": "trunk",
    "vlans": "1,12,200,300,600"
}
```
### Interface tagging on target device
Route parameters: interface to configure
Body parameters: 
    - ip (ip of the devices to be queried) 
    - vlan_ids (vlan id the be setted or replaced) type: str (vlan ids are separated by a comma 1,200,300)
    - append (append vlan_ids or replace them)
```
curl --location 'http://localhost:8080/switch/interfaces/Te1%2F0%2F45/vlan-tag' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
    "ip":"10.255.3.1",
    "vlan_ids": "680",
    "append": true
}' 
```
Expected output
```
{
    "mode": "trunk",
    "vlans": "1,12,200,300,680"
}
```

