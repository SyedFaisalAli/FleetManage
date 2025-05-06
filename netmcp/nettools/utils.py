import netifaces
import configparser
import io
from typing import Dict, Any


def dict_to_ini_string(config_dict: Dict[str, Dict[str, Any]]) -> str:
    """
    Converts a nested dictionary into a string formatted as an INI file
    using configparser.

    Args:
        config_dict: A dictionary where top-level keys are section names
                     (strings), and their values are dictionaries of key-value
                     pairs for that section. Values will be converted to strings.

                     Example:
                     {
                         'Match': {
                             'Name': 'eth0',
                             'Type': 'ether'
                         },
                         'Network': {
                             'DHCP': 'yes',
                             'Address': '192.168.1.100/24'
                         }
                     }

    Returns:
        A string containing the configuration in INI format.
    """
    # Create a ConfigParser object.
    # allow_no_value=True: Allows keys without values (e.g., [Section]\nKey\n[Section2])
    # delimiters=('='): Use '=' as the key-value separator, common in INI/systemd
    config = configparser.ConfigParser(delimiters=('='))

    # Iterate through the input dictionary
    for section, keys in config_dict.items():
        # Add each top-level key as a section
        # Avoid trying to add the default section explicitly if named '[DEFAULT]'
        if section != configparser.DEFAULTSECT:
             # Ensure section name is a string
             config.add_section(str(section))

        # Add key-value pairs to the current section
        for key, value in keys.items():
            # configparser.set expects strings for key and value.
            # Convert both to string explicitly.
            config.set(str(section), str(key), str(value))

    # Use io.StringIO to capture the output of config.write() into a string
    # StringIO acts like a text file in memory
    with io.StringIO() as string_buffer:
        # Write the configuration to the buffer
        config.write(string_buffer)
        # Get the accumulated string from the buffer
        ini_string = string_buffer.getvalue()

    return ini_string


def get_default_interface():
    """
    Retrieves the default network interface using netifaces.

    Returns:
        str or None: The name of the default network interface (e.g., 'eth0', 'wlan0')
                     or None if no default interface is found.
    """
    try:
        ip, interface, _ = netifaces.gateways()[netifaces.AF_INET][0]
        return interface
    except (KeyError, IndexError):
        # No default interface found
        return None

def get_mac_address(interface):
    """
    Retrieves the MAC address of a given network interface using netifaces.

    Args:
        interface (str): The name of the network interface (e.g., 'eth0', 'wlan0').

    Returns:
        str or None: The MAC address as a string (e.g., '00:11:22:33:44:55')
                     or None if the interface doesn't exist or the MAC address
                     cannot be retrieved.
    """
    try:
        addresses = netifaces.ifaddresses(interface)
        mac_address_list = addresses[netifaces.AF_PACKET]
        if mac_address_list and 'addr' in mac_address_list[0]:
            return mac_address_list[0]['addr']
    except ValueError:
        # Interface does not exist
        return None
    except KeyError:
        # AF_LINK (usually representing MAC address) is not present for this interface
        return None
    return None

def get_default_gateway():
    """
    Retrieves the default gateway address

    Returns:
        str or None: The gateway address as a string (e.g., '192.168.1.1')
                        or None if there is no default route.
    """
    default_gateways = netifaces.default_gateway()
    default_gw_ip = None
    # Format default gateway information
    for family, (gateway, interface) in default_gateways.items():
        if family == netifaces.AF_INET or family == netifaces.AF_INET6:
            return gateway
    
    return None
