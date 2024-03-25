import logging

from swagger_server.utils.mac_conversion import format_mac
from scrapli.helper import genie_parse
from swagger_server.driver.singleton_driver import SingletonArgs
from swagger_server.models.exceptions import DeviceNotHandled
from swagger_server.utils.credentials_handler import get_credentials
from CiscoInterfaceNameConverter import converter
from swagger_server.models.interface_switchport_configuration_information import InterfaceSwitchportConfigurationInformation
from scrapli.driver.core import IOSXEDriver

from swagger_server.utils.vlan_syntax_converter import adjust_vlan_set, range_unroller, unroll_vlans

PLATFORM = "cisco_iosxe"

class CiscoIosXeSsh(metaclass=SingletonArgs):
    """Singleton class that extract data from a Cisco IOS XE switch using ssh.
    
    :param device_ip: The IP address of the switch to be controlled.
    :type device_ip: str
    """

    def __init__(self, device_ip):
        """Constructor method

        :raises DeviceNotHandled: If the credentials associated with the controlled 
        device are not present in the environment variables or in the credential manager (Vault).
        """
        logging.debug(f"Create ssh driver for device {device_ip}")
        try: 
            credentials = get_credentials(device_ip=device_ip)
            self.__device = {
                "host": device_ip,
                "auth_username": credentials.get('username'),
                "auth_password": credentials.get('password'),
                "auth_strict_key": False,
            #    "transport": "ssh2",
                "ssh_config_file": True,
                "timeout_socket": 5
            }
        except:
            del self
            raise DeviceNotHandled("The service does not handle the specified device")
            

    def get_version_info(self):
        with IOSXEDriver(**self.__device) as device_connection:
            platform_information = device_connection.send_command("sh version")
            logging.debug(f"[SHOW Hardware] scrapli {platform_information.result}")
            try:
                res = platform_information.genie_parse_output()['version']
                res_filtered = {key: res.get(key) for key in ["hostname", "chassis", "chassis_sn", "platform", "image_id", "version"]}
                return res_filtered
            except Exception as e:
                logging.error("[PARSING ERROR]", e)
                return None


    def get_interface_configuration_information(self, interface_name):
        with IOSXEDriver(**self.__device) as device_connection:
            interface_name = interface_name.replace('=', '')
            switchport_information = device_connection.send_command(f"show interfaces {interface_name} switchport")
            switchport_information = switchport_information.genie_parse_output()[converter.convert_interface(interface_name=interface_name, return_long=True)]
            mode = switchport_information.get('operational_mode', switchport_information['switchport_mode'])
            vlans = switchport_information.get('access_vlan') if mode == 'access' else switchport_information.get('trunk_vlans')
            vlans = "1-4094" if vlans == "all" else vlans
            return InterfaceSwitchportConfigurationInformation(mode=mode, vlans=unroll_vlans(vlans))
        

    def get_vlan_list(self):
        with IOSXEDriver(**self.__device) as device_connection:
            vlan_list = (device_connection.send_command("sh vlan")).genie_parse_output()
            return [{'id': int(vlan_id), 'name': vlan_info.get('name', '')} for vlan_id, vlan_info in vlan_list['vlans'].items()]
    


    def interface_mode(self, switchport_mode, interface_name):
        with IOSXEDriver(**self.__device) as device_connection:
            device_connection.send_configs([f"interface {interface_name}", f"switchport mode {switchport_mode}"])

    def tag_interface(self, interface_name, vlan_id, append):
        with IOSXEDriver(**self.__device) as device_connection:
            interface_info = self.get_interface_configuration_information(interface_name)
            vlans = vlan_id + "," + interface_info.vlans if append else vlan_id
            add_vlan_command = f"switchport trunk allowed vlan {adjust_vlan_set(vlans)}" if interface_info.mode == "trunk" else f"switchport access vlan {vlans}"
            device_connection.send_configs([f"interface {interface_name}", add_vlan_command])
            
            return {"mode": interface_info.mode, "vlans": adjust_vlan_set(vlans) if interface_info.mode == "trunk" else vlan_id}, 200
        
    def untag_interface(self, interface_name, vlan_id):
        with IOSXEDriver(**self.__device) as device_connection:
            interface_info = self.get_interface_configuration_information(interface_name)
            remove_vlan_command = f"no switchport trunk allowed vlan {vlan_id}" if interface_info.mode == "trunk" else f"no switchport access vlan {vlan_id}"
            device_connection.send_configs([f"interface {interface_name}", remove_vlan_command])
            
            return 200
