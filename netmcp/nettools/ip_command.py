#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - IP Command Tool

This module implements the IP command diagnostic tool for NetAssist.
"""

import logging
import netifaces
import socket
import ipaddress
import subprocess
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("netmcp")

async def run_ip_command_impl(command: str, interface: str = "", ctx = None) -> Dict[str, Any]:
    """
    Run ip commands (addr, link, route) with interpretation using netifaces.
    
    Args:
        command: The ip subcommand to run (addr, link, route)
        interface: Optional interface name to filter results
        ctx: The MCP context
        
    Returns:
        Dict containing the network information and interpretation
    """
    
    if command not in ["addr", "link", "route"]:
        return {
            "success": False,
            "error": f"Invalid command: {command}. Must be one of: addr, link, route"
        }
    
    logger.info(f"Getting {command} information for interface '{interface or 'all'}'")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info(f"Getting {command} information for {interface or 'all interfaces'}")
    
    try:
        # Get all available interfaces
        if ctx:
            await ctx.report_progress(20, 100)
            await ctx.info("Retrieving network interfaces")
        
        all_interfaces = netifaces.interfaces()
        
        # Filter by interface if specified
        interfaces_to_process = [interface] if interface and interface in all_interfaces else all_interfaces
        
        if interface and interface not in all_interfaces:
            return {
                "success": False,
                "message": f"Interface {interface} not found",
                "error": "Interface not found"
            }
        
        if ctx:
            await ctx.report_progress(40, 100)
            await ctx.info(f"Processing {len(interfaces_to_process)} interfaces")
        
        result_data = []
        
        # Process based on command
        if command == "addr":
            # Get address information for each interface
            for iface in interfaces_to_process:
                iface_data = {"name": iface, "addresses": []}
                
                # Get addresses by family
                addrs = netifaces.ifaddresses(iface)
                
                # IPv4 addresses
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr:
                            netmask = addr.get('netmask', '255.255.255.0')
                            prefix_len = sum(bin(int(x)).count('1') for x in netmask.split('.'))
                            iface_data["addresses"].append({
                                "type": "ipv4",
                                "address": f"{addr['addr']}/{prefix_len}"
                            })
                
                # IPv6 addresses
                if netifaces.AF_INET6 in addrs:
                    for addr in addrs[netifaces.AF_INET6]:
                        if 'addr' in addr:
                            # Remove scope id if present
                            ipv6_addr = addr['addr'].split('%')[0]
                            prefix_len = addr.get('prefixlen', 64)
                            iface_data["addresses"].append({
                                "type": "ipv6",
                                "address": f"{ipv6_addr}/{prefix_len}"
                            })
                
                # MAC address
                if netifaces.AF_PACKET in addrs and addrs[netifaces.AF_PACKET]:
                    mac = addrs[netifaces.AF_PACKET][0].get('addr')
                    if mac:
                        iface_data["mac"] = mac
                
                result_data.append(iface_data)
            
            # Generate interpretation
            if interface:
                addr_count = len(result_data[0]["addresses"]) if result_data else 0
                interpretation = f"Interface {interface} has {addr_count} IP address(es)"
            else:
                total_interfaces = len(result_data)
                total_addresses = sum(len(iface["addresses"]) for iface in result_data)
                interpretation = f"Found {total_interfaces} interfaces with a total of {total_addresses} IP addresses"
        
        elif command == "link":
            # Get link information for each interface
            import psutil
            
            # Get interface statistics from psutil
            net_stats = psutil.net_if_stats()
            
            for iface in interfaces_to_process:
                iface_data = {"name": iface}
                
                # Get MAC address
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_PACKET in addrs and addrs[netifaces.AF_PACKET]:
                    mac = addrs[netifaces.AF_PACKET][0].get('addr')
                    if mac:
                        iface_data["mac"] = mac
                
                # Get interface status from psutil
                if iface in net_stats:
                    stats = net_stats[iface]
                    iface_data["state"] = "UP" if stats.isup else "DOWN"
                    iface_data["speed"] = f"{stats.speed} Mbps" if stats.speed > 0 else "Unknown"
                    iface_data["mtu"] = stats.mtu
                    iface_data["duplex"] = stats.duplex if hasattr(stats, 'duplex') else "Unknown"
                
                result_data.append(iface_data)
            
            # Generate interpretation
            if interface:
                if result_data:
                    state = result_data[0].get("state", "UNKNOWN")
                    mac = result_data[0].get("mac", "Unknown MAC")
                    interpretation = f"Interface {interface} is {state} with MAC address {mac}"
                else:
                    interpretation = f"No link information available for interface {interface}"
            else:
                up_count = sum(1 for iface in result_data if iface.get("state") == "UP")
                down_count = sum(1 for iface in result_data if iface.get("state") == "DOWN")
                interpretation = f"Found {len(result_data)} interfaces: {up_count} up, {down_count} down"
        
        elif command == "route":
            # Get routing information
            
            # For routes, we still need to use subprocess as netifaces doesn't provide full routing info
            if ctx:
                await ctx.info("Using subprocess for route information (not fully supported by netifaces)")
            
            # Get default gateways
            default_gateways = netifaces.default_gateway()
            
            # Format default gateway information
            for family, (gateway, interface) in default_gateways.items():
                if family == netifaces.AF_INET:
                    result_data.append({
                        "type": "default",
                        "family": "ipv4",
                        "via": gateway,
                        "dev": interface
                    })
                elif family == netifaces.AF_INET6:
                    result_data.append({
                        "type": "default",
                        "family": "ipv6",
                        "via": gateway,
                        "dev": interface
                    })
            
            # Try to get more detailed route information using subprocess
            # This is a fallback since netifaces doesn't provide full routing table
            try:
                cmd = ["ip", "route", "show"]
                if interface:
                    cmd.extend(["dev", interface])
                
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if process.returncode == 0:
                    # Parse the output to extract routes
                    for line in process.stdout.splitlines():
                        if line.startswith("default via"):
                            # Skip default routes as we already have them from netifaces
                            continue
                        
                        parts = line.split()
                        if len(parts) >= 3 and parts[1] == "dev":
                            result_data.append({
                                "type": "network",
                                "dest": parts[0],
                                "dev": parts[2]
                            })
            except Exception as e:
                # If subprocess fails, we'll just use the default gateway information
                logger.warning(f"Could not get detailed routing information: {e}")
            
            # Filter by interface if specified
            if interface:
                result_data = [route for route in result_data if route.get("dev") == interface]
            
            # Generate interpretation
            default_routes = [route for route in result_data if route.get("type") == "default"]
            if interface:
                if default_routes:
                    gateway_ips = [route.get("via") for route in default_routes]
                    interpretation = f"Interface {interface} has default route(s) via {', '.join(gateway_ips)}"
                elif result_data:
                    interpretation = f"Interface {interface} has {len(result_data)} routes but no default route"
                else:
                    interpretation = f"No routes found for interface {interface}"
            else:
                if default_routes:
                    gateway_info = [f"{route.get('via')} ({route.get('family')}) on {route.get('dev')}"
                                   for route in default_routes]
                    interpretation = f"Default route(s): {', '.join(gateway_info)}"
                    if len(result_data) > len(default_routes):
                        interpretation += f". {len(result_data) - len(default_routes)} additional routes configured"
                else:
                    interpretation = f"No default route found. {len(result_data)} network routes configured"
        
        if ctx:
            await ctx.report_progress(80, 100)
            await ctx.info(f"Completed processing {command} information")
        
        result = {
            "success": True,
            "command": f"ip {command} {interface}".strip(),
            "parsed_data": result_data,
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Command complete: {interpretation}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting {command} information: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": f"Failed to get {command} information",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)