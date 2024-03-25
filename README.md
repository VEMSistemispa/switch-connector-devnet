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
