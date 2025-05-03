#!/usr/bin/env python3
"""
Network Diagnostics MCP Server

This module implements a FastMCP server that provides network diagnostic tools
for the Fleet Management system, focusing on systemd-networkd.
"""

import logging
import sys
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP, Context

# Import tool implementations
from nettools import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("network_diagnostics_server")

# Create the FastMCP server
server = FastMCP(
    name="network-diagnostics",
    instructions="Network diagnostics MCP server on device network management."
)

@server.tool(
    description="Get the default interface for the system"
)
async def get_default_interface(ctx: Context = None) -> Dict[str, Any]:
    """
    Get the default interface for the system.
    
    Args:
        ctx: The MCP context
        
    Returns:
        Dict containing the default interface name and its details
    """
    return await get_default_network_interface_impl(ctx)

@server.tool(
    description="Ping a host and interpret the results with latency statistics and packet loss"
)
async def run_ping(host: str = "8.8.8.8", count: int = 4, ctx: Context = None) -> Dict[str, Any]:
    """
    Ping a host and interpret the results.
    
    Args:
        host: The hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
        ctx: The MCP context
        
    Returns:
        Dict containing the ping results and interpretation
    """
    return await run_ping_impl(host, count, ctx)

@server.tool(
    description="Run ip commands (addr, link, route) with interpretation"
)
async def run_ip_command(command: str, interface: str = "", ctx: Context = None) -> Dict[str, Any]:
    """
    Run ip commands (addr, link, route) with interpretation.
    
    Args:
        command: The ip subcommand to run (addr, link, route)
        interface: Optional interface name to filter results
        ctx: The MCP context
        
    Returns:
        Dict containing the command output and interpretation
    """
    return await run_ip_command_impl(command, interface, ctx)

@server.tool(
    description="Show listening ports and their status"
)
async def run_netstat(options: str = "tuln", ctx: Context = None) -> Dict[str, Any]:
    """
    Show network connections and statistics.
    
    Args:
        options: Netstat options (e.g., 'tuln' for TCP/UDP listening sockets)
        ctx: The MCP context
        
    Returns:
        Dict containing the netstat output and interpretation
    """
    return await run_netstat_impl(options, ctx)

# @server.tool(
#     description="Read and parse systemd-networkd configuration files of interfaces."
# )
# async def read_networkd_config(interface: str = "", ctx: Context = None) -> Dict[str, Any]:
#     """
#     Read and parse systemd-networkd configuration files.
    
#     Args:
#         interface: Optional interface name to filter results
#         ctx: The MCP context
        
#     Returns:
#         Dict containing the parsed configuration
#     """
#     return await read_networkd_config_impl(interface, ctx)

@server.tool(
    description="List all network interfaces with their status"
)
async def list_network_interfaces(ctx: Context = None) -> Dict[str, Any]:
    """
    List all network interfaces with their status.
    
    Args:
        ctx: The MCP context
        
    Returns:
        Dict containing the list of interfaces and their status
    """
    return await list_network_interfaces_impl(ctx)

@server.tool(
    description="Run a series of tests to diagnose connectivity issues"
)
async def diagnose_connectivity(target: str = "8.8.8.8", ctx: Context = None) -> Dict[str, Any]:
    """
    Run a series of tests to diagnose connectivity issues.
    
    Args:
        target: Target host to test connectivity to
        ctx: The MCP context
        
    Returns:
        Dict containing the diagnostic results
    """
    return await diagnose_connectivity_impl(target, ctx)

def main():
    """Entry point for the MCP server."""
    try:
        # Run the server
        logger.info("Starting Network Diagnostics MCP Server")
        server.run("sse", host="127.0.0.1", port=8888, log_level="debug")
        return 0
    except KeyboardInterrupt:
        logger.info("Server interrupted, exiting...")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())