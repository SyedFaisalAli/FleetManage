import netifaces
import os

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
