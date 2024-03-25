import json
import logging
import urllib.parse
import requests
from swagger_server.driver.singleton_driver import SingletonArgs
from swagger_server.models.interface_switchport_configuration_information import InterfaceSwitchportConfigurationInformation
from swagger_server.utils.mac_conversion import *

from swagger_server.models.exceptions import DeviceNotHandled
from swagger_server.utils.credentials_handler import get_credentials
from CiscoInterfaceNameConverter import converter
from swagger_server.utils.vlan_syntax_converter import adjust_vlan_set, remove_vlan_from_set, unroll_vlans

ACCEPT_HEADER = 'application/yang-data+json'
CONTENT_TYPE_HEADER = 'application/yang-data+json'
DEFAULT_TIMEOUT = 5


class CiscoIosXeREST(metaclass=SingletonArgs):
    """Singleton class that extract data from a Cisco IOS XE switch using restconf.
    
    :param device_ip: The IP address of the switch to be controlled.
    :type device_ip: str
    """
    
    def __init__(self, device_ip):
        """Constructor method

        :raises DeviceNotHandled: If the credentials associated with the controlled 
        device are not present in the environment variables or in the credential manager (Vault).
        """
        logging.debug(f"Create restconf driver for device {device_ip}")
        try: 
            credentials = get_credentials(device_ip=device_ip)
            self.__device_ip = device_ip
            self.__username = credentials.get('username')
            self.__device_password = credentials.get('password')
        except:
            del self
            raise DeviceNotHandled(f"The service does not handle the specified device. Crediantal for device {device_ip} not available")
    

    def get_hostname(self):
        logging.debug(f"Fetching hostname for: {self.__device_ip}")
        response = requests.get(url='https://%s/restconf/data/Cisco-IOS-XE-native:native/hostname' % self.__device_ip, headers={'Accept': ACCEPT_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                verify=False, timeout=DEFAULT_TIMEOUT)

        if not response.ok:
            logging.error(f"An error occurred while gathering hostname for device {self.__device_ip}.")
            response.raise_for_status()

        res = response.json()
        return {
            'hostname': res['Cisco-IOS-XE-native:hostname']
        }

    def get_hardware_data(self):
        logging.debug(f"Fetching hardware info for: {self.__device_ip}")
        response = requests.get(url='https://%s/restconf/data/Cisco-IOS-XE-device-hardware-oper:device-hardware-data/device-hardware' % self.__device_ip, headers={'Accept': ACCEPT_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                verify=False, timeout=DEFAULT_TIMEOUT)

        if not response.ok:
            logging.error(f"An error occurred while gathering hardware data for device {self.__device_ip}.")
            response.raise_for_status()

        res = response.json()['Cisco-IOS-XE-device-hardware-oper:device-hardware']
        device_inventory = res['device-inventory'][0]
        software_version = res['device-system-data']['software-version']
        
        try:
            match = re.split(r',\s*', software_version)
            platform = re.split(r'\sSoftware\s*', match[1])[0]
            image_id = re.split(r'\sSoftware\s*', match[1])[1][1:-1]
            version = re.split(r'Version\s*', match[2])[1]
            
            return {
                'chassis': device_inventory['part-number'],
                'chassis_sn': device_inventory['serial-number'],
                'platform': platform,
                'image_id': image_id,
                'version': version
            }
        except Exception:
            return None


    def get_interface_configuration_information(self, interface_name):
        long_interface = converter.convert_interface(interface_name=interface_name, return_long=True)
        regex = r'^([^\d]+)(\d+.*)$'
        splitted_interface = re.search(regex, long_interface)
        url_encoded_interface_number = urllib.parse.quote_plus(splitted_interface[2])
        response = requests.get(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport-config/switchport", 
                        headers={'Accept': ACCEPT_HEADER}, 
                        auth=(self.__username, self.__device_password),
                        verify=False, timeout=DEFAULT_TIMEOUT)
        if not response.ok: 
            if response.status_code == 404:
                response = requests.get(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport", 
                                headers={'Accept': ACCEPT_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                verify=False)
            response.raise_for_status()
        try:
            response = response.json()
            switchport_parameters = response['Cisco-IOS-XE-native:switchport']
            mode = list(switchport_parameters['Cisco-IOS-XE-switch:mode'].keys())[0]
            vlans = "1" if mode == 'access' and 'Cisco-IOS-XE-switch:access' not in switchport_parameters else \
            str(switchport_parameters['Cisco-IOS-XE-switch:access']['vlan']['vlan']) if mode == 'access' and 'Cisco-IOS-XE-switch:access' in switchport_parameters else \
            "1-4094" if mode == 'trunk' and "Cisco-IOS-XE-switch:trunk" not in switchport_parameters else \
            str(switchport_parameters['Cisco-IOS-XE-switch:trunk']['allowed']['vlan']['vlans'])
            return InterfaceSwitchportConfigurationInformation(mode=mode, vlans=unroll_vlans(vlans))
        except Exception as e:
            logging.error(f"An error occurred while retrieving configuration information for interface {interface_name} on device {self.__device_ip}.")
            raise e

    
    def get_vlan_list(self):
        response = requests.get(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/vlan/Cisco-IOS-XE-vlan:vlan-list", 
                        headers={'Accept': ACCEPT_HEADER}, 
                        auth=(self.__username, self.__device_password),
                        verify=False, timeout=DEFAULT_TIMEOUT)
        if not response.ok:
            logging.error(f"An error occured while retrieving vlan DB list from device {self.__device_ip}")
            response.raise_for_status()
        else:
            vlan_list = response.json()["Cisco-IOS-XE-vlan:vlan-list"]
            return [{
                "id": vlan['id'],
                "name": vlan.get('name', f"VLAN{vlan['id']:04d}")
            } for vlan in vlan_list] + [{"id": 1, "name": "default"}]
            
    def interface_mode(self, switchport_mode, interface_name):
        if switchport_mode in ['trunk', 'access']:
            body = json.dumps({
                        "Cisco-IOS-XE-switch:mode": {
                            switchport_mode: {}
                        }
                    })
            long_interface = converter.convert_interface(interface_name=interface_name, return_long=True)
            regex = r'^([^\d]+)(\d+.*)$'
            splitted_interface = re.search(regex, long_interface)
            url_encoded_interface_number = urllib.parse.quote_plus(splitted_interface[2])
            response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport/mode",
                            headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER},
                            auth=(self.__username, self.__device_password),
                            data=body,
                            verify=False, timeout=DEFAULT_TIMEOUT)
            if not response.ok:
                logging.error(f"An error occured while changing interface mode to {switchport_mode} on interface {interface_name} on device {self.__device_ip}")
                response.raise_for_status()
            else:
                logging.info(f"Interface mode switched to {switchport_mode} on {interface_name} on device {self.__device_ip}")
                return {"result" : f"Interface mode changed successfully to {switchport_mode} on {interface_name} on device {self.__device_ip}"}, 200
        else:
            return {"result:" : f"Interface switchport mode [{switchport_mode}] invalid. Must be trunk or access."}, 400


    def tag_interface(self, interface_name, vlan_id, append):
        interface_info = self.get_interface_configuration_information(interface_name)
        long_interface = converter.convert_interface(interface_name=interface_name, return_long=True)
        regex = r'^([^\d]+)(\d+.*)$'
        splitted_interface = re.search(regex, long_interface)
        url_encoded_interface_number = urllib.parse.quote_plus(splitted_interface[2])
        logging.info(f"Attempting tagging interface {interface_name} with vlan [{vlan_id}] on device DEVICE {self.__device_ip}")
        if interface_info.mode == "trunk":
            vlans = adjust_vlan_set(vlan_id + "," + interface_info.vlans if append else vlan_id)
            body = json.dumps({
                        "Cisco-IOS-XE-switch:trunk": {
                            "allowed": {
                                "vlan": {
                                    "vlans": vlans
                                }
                            }
                        }
                    })
            response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport-config/switchport/trunk",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
            if not response.ok:
                #Fallback on switchport (no switchport-config) for Catalyst 3850
                logging.error(f"An error occured in tagging interface {interface_name} mode {interface_info.mode} with vlans [{vlans}] on device {self.__device_ip}")
                logging.info(f"Proceding with fallback procedure...")
                response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport/trunk",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
            
                if response and not response.ok:
                    logging.error(f"Fallback failed.")
                    response.raise_for_status()
            
            logging.info(f"Successfully tagged interface {interface_name} with vlans [{vlans}] on device {self.__device_ip}")
            return {"mode": "trunk", "vlans": vlans}, 200
        
        elif interface_info.mode == "access":
            body = json.dumps({
                        "Cisco-IOS-XE-switch:access": {
                            "vlan": {
                                "vlan": vlan_id
                            }
                        }
                    })
            response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport-config/switchport/access",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER},
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
            if not response.ok:
                #Fallback on switchport (no switchport-config) for Catalyst 3850
                logging.error(f"An error occured in tagging interface {interface_name} mode {interface_info.mode} with vlan [{vlan_id}] on device {self.__device_ip}")
                logging.info(f"Proceding with fallback procedure...")
                response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport/access",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER},
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
                if not response.ok:
                    logging.error(f"Fallback failed.")
                    response.raise_for_status()
            
            logging.info(f"Successfully tagged interface {interface_name} mode {interface_info.mode} with vlan [{vlan_id}] on device DEVICE {self.__device_ip}")
            return {"mode": "access", "vlans": vlan_id}, 200
        
        return {"status:":"Unexpected error"}, 502

    def untag_interface(self, interface_name, vlan_id):
        interface_info = self.get_interface_configuration_information(interface_name)
        long_interface = converter.convert_interface(interface_name=interface_name, return_long=True)
        regex = r'^([^\d]+)(\d+.*)$'
        splitted_interface = re.search(regex, long_interface)
        url_encoded_interface_number = urllib.parse.quote_plus(splitted_interface[2])
        logging.info(f"Attempting UNTagging interface {interface_name} ofs {vlan_id} on device DEVICE {self.__device_ip}")
        if interface_info.mode == "trunk":
            logging.debug(f"Untag {self.__device_ip} | {interface_name} | present vlans: {interface_info.vlans} removing: {vlan_id}")
            adjusted_vlans = remove_vlan_from_set(interface_info.vlans, int(vlan_id))
            body = json.dumps({
                        "Cisco-IOS-XE-switch:trunk": {
                            "allowed": {
                                "vlan": {
                                    "vlans": adjusted_vlans
                                }
                            }
                        }
                    })
            response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport-config/switchport/trunk",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
            if not response.ok:
                #Fallback on switchport (no switchport-config) for Catalyst 3850
                logging.error(f"An error occured in UNTagging interface {interface_name} mode {interface_info.mode} of vlan [{vlan_id}] on device {self.__device_ip}")
                logging.info(f"Proceding with fallback procedure...")
                response = requests.patch(f"https://{self.__device_ip}/restconf/data/Cisco-IOS-XE-native:native/interface/{splitted_interface[1]}={url_encoded_interface_number}/switchport/trunk",
                                headers={'Accept': ACCEPT_HEADER, 'Content-type': CONTENT_TYPE_HEADER}, 
                                auth=(self.__username, self.__device_password),
                                data=body,
                                verify=False, timeout=DEFAULT_TIMEOUT)
                if not response.ok:
                    logging.error(f"Fallback failed.")
                    response.raise_for_status()
            
            logging.info(f"Successfully UNTagged interface {interface_name} of vlan [{vlan_id}] on device {self.__device_ip}")
            return {
                    "result": f'Vlan {vlan_id} removed from interface {interface_name} on device {self.__device_ip}'
                }, 200
        else:
            return {"status:": f"Interface {interface_name} on device {self.__device_ip} not in trunk mode."}, 502
