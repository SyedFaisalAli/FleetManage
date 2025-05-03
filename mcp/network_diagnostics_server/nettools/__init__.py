"""
Network Diagnostics MCP Server - Nettools Package

This package contains the network diagnostic tool implementations for the Fleet Management system.
"""

# Import all tool implementations to make them available from the package
from .ping import run_ping_impl
from .ip_command import run_ip_command_impl
from .netstat import run_netstat_impl
from .networkd_config import read_networkd_config_impl
from .network_interfaces import list_network_interfaces_impl, get_default_network_interface_impl
from .connectivity_diagnostics import diagnose_connectivity_impl
from .utils import get_mac_address

# Define what's available when using "from nettools import *"
__all__ = [
    'run_ping_impl',
    'run_ip_command_impl',
    'run_netstat_impl',
    'read_networkd_config_impl',
    'list_network_interfaces_impl',
    'diagnose_connectivity_impl',
    'get_default_network_interface_impl',
    'get_mac_address'
]