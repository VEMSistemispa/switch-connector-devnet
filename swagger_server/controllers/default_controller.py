import logging
import connexion
from scrapli.exceptions import ScrapliAuthenticationFailed, ScrapliConnectionError
from swagger_server.utils.credentials_handler import update_credentials
from swagger_server.driver.cisco_ios_xe_restconf import CiscoIosXeREST
from swagger_server.driver.cisco_ios_xe_ssh import CiscoIosXeSsh

RESTCONF_EXCEPTION_TEXT = "An error occurred in RESTCONF with {device_ip} device. Details: {error_detail}"
NOT_A_JSON_EXCEPTION_TEXT = "Received a request with mime-type different from application/json"

async def update_device_inventory():  # noqa: E501
    global inventory
    """update inventory of devices

    update inventory of devices
    :rtype: None
    """
    if connexion.request.is_json:
        inventory = connexion.request.get_json()
        update_credentials(inventory)
        return 'Inventory updated successfully', 200
    return 'Internal server error', 500
        
def get_hardware_info(ip):
    """get hardware info of the switch.

    Retrieve base serial number and model number for the specified switch.  

    :param ip: Ipv4 of the switch to query
    :type ip: dict | bytes

    :rtype: Object
    """
    try:
        logging.debug(f"Try to fetch hardware info for: {ip} with restconf")
        hostname = CiscoIosXeREST(ip).get_hostname()
        hardware_data = CiscoIosXeREST(ip).get_hardware_data()
        hardware_data.update(hostname)
        hardware_data['management_protocol'] = "RESTCONF"
        return hardware_data
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        logging.debug(f"Try to fetch hardware info for: {ip} with ssh")

        try:
            res = CiscoIosXeSsh(ip).get_version_info()
            res['management_protocol'] = "SSH"
            return res
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout gathering info from: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was an error gathering info to: {ip} with ssh")
            raise e


def get_interface_configuration_information(ip, interface_name):
    """get all configuration information associated with a switch interface.

    Retrieve interface configuration information for the specified switch.          

    :param ip: Ipv4 of the switch to query
    :type ip: dict | bytes
    :param interface_name: Full name of the desired interface
    :type interface_name: str

    :rtype: InterfacesConfigurationInformation
    """      
    try:
        logging.debug(f"Try to fetch interface {interface_name} configuration for: {ip} with restconf")
        return CiscoIosXeREST(ip).get_interface_configuration_information(interface_name=interface_name)
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        logging.debug(f"Try to fetch interface {interface_name} configuration for: {ip} with ssh")

        try:
            res = CiscoIosXeSsh(ip).get_interface_configuration_information(interface_name=interface_name)
            return res
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout gathering info from: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was an error gathering info to: {ip} with ssh")
            raise e


def get_vlan_list(ip):
    try:
        logging.debug(f"Try to fetch vlan list for: {ip} with restconf")
        return CiscoIosXeREST(ip).get_vlan_list()
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        logging.debug(f"Try to fetch vlan list for: {ip} with ssh")

        try:
            res = CiscoIosXeSsh(ip).get_vlan_list()
            return res
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout gathering info from: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was an error gathering info to: {ip} with ssh")
            raise e


def switch_port_mode(ip, mode, interface_name):
    try:
        logging.debug(f"Try to change switch port mode for: {ip} on {interface_name} with restconf")
        return CiscoIosXeREST(ip).interface_mode(mode, interface_name)
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        logging.debug(f"Try to change switch port mode for: {ip} on {interface_name} with ssh")
        try:
            return CiscoIosXeSsh(ip).interface_mode(mode, interface_name)
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout on: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was an error on: {ip} with ssh")
            raise e


def tag_interface(interface_name):
    if not connexion.request.is_json:
        logging.error(NOT_A_JSON_EXCEPTION_TEXT)
        raise TypeError(NOT_A_JSON_EXCEPTION_TEXT)
    body = connexion.request.get_json()
    ip = body.get("ip")
    vlan_ids = body.get("vlan_ids")
    append = body.get("append", None)
    try:
        logging.debug(f"Try to tag switch interface for: {ip} on {interface_name} with restconf")
        return CiscoIosXeREST(ip).tag_interface(interface_name, vlan_ids, append)
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        try:
            logging.debug(f"Try to tag switch interface for: {ip} on {interface_name} with SSH")
            return CiscoIosXeSsh(ip).tag_interface(interface_name, vlan_ids, append)
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout on: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was on: {ip} with ssh")
            raise e

def untag_interface(ip, interface_name, vlan_id):
    try:
        logging.debug(f"Try to untag vlan {vlan_id} for {ip} on {interface_name} with restconf")
        return CiscoIosXeREST(ip).untag_interface(interface_name, vlan_id)
    except Exception as e:
        logging.error(RESTCONF_EXCEPTION_TEXT.format(
            device_ip=ip, error_detail=str(e)))
        try:
            logging.debug(f"Try to untag vlan {vlan_id} for {ip} on {interface_name} with with SSH")
            return CiscoIosXeSsh(ip).untag_interface(interface_name, vlan_id)
        except (ScrapliAuthenticationFailed, ScrapliConnectionError) as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"Timout on: {ip} with ssh")
            return None, 504
        except Exception as e:
            logging.error(RESTCONF_EXCEPTION_TEXT.format(device_ip=ip, error_detail=str(e)))
            logging.debug(f"There was an error on: {ip} with ssh")
            raise e