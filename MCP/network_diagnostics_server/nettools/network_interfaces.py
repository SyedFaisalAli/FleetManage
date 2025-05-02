#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Network Interfaces Tool

This module implements the network interfaces listing tool for the Fleet Management system.
"""

import logging
import netifaces
import psutil
from typing import Dict, List, Any, Optional
from .utils import get_default_interface 

# Configure logging
logger = logging.getLogger("network_diagnostics_server")

async def get_default_network_interface_impl(ctx = None) -> Dict[str, Any]:
    """
    Get the default network interface for the system.
    
    Args:
        ctx: The MCP context
        
    Returns:
        Dict containing the default network interface name
    """
    
    logger.info("Getting default network interface")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info("Getting default network interface")
    
    try:
        # Get the default network interface
        default_iface = get_default_interface()
        
        if ctx:
            await ctx.report_progress(100, 100)
        
        return {
            "success": True,
            "default_interface": default_iface
        }
        
    except Exception as e:
        error_msg = f"Error getting default network interface: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": "Failed to get default network interface",
            "error": str(e)
        }

async def list_network_interfaces_impl(ctx = None) -> Dict[str, Any]:
    """
    List all network interfaces with their status.
    
    Args:
        ctx: The MCP context
        
    Returns:
        Dict containing the list of interfaces and their status
    """
    
    logger.info("Listing network interfaces")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info("Listing network interfaces")
    
    try:
        # Get all network interfaces
        if ctx:
            await ctx.report_progress(20, 100)
            await ctx.info("Getting network interfaces")
        
        interfaces = netifaces.interfaces()
        
        # Get interface statistics from psutil
        if ctx:
            await ctx.report_progress(40, 100)
            await ctx.info("Getting interface statistics")
        
        net_stats = psutil.net_if_stats()
        
        # Process each interface
        result_interfaces = []
        for iface in interfaces:
            interface_info = {
                "name": iface,
                "addresses": [],
                "status": "down",
                "type": "unknown"
            }
            
            # Get interface status from psutil
            if iface in net_stats:
                stats = net_stats[iface]
                interface_info["status"] = "up" if stats.isup else "down"
                interface_info["mtu"] = stats.mtu
                if hasattr(stats, 'speed') and stats.speed > 0:
                    interface_info["speed"] = f"{stats.speed} Mbps"
                if hasattr(stats, 'duplex'):
                    interface_info["duplex"] = stats.duplex
            
            # Get addresses by family
            addrs = netifaces.ifaddresses(iface)
            
            # IPv4 addresses
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if 'addr' in addr:
                        netmask = addr.get('netmask', '255.255.255.0')
                        prefix_len = sum(bin(int(x)).count('1') for x in netmask.split('.'))
                        interface_info["addresses"].append(f"{addr['addr']}/{prefix_len}")
            
            # IPv6 addresses
            if netifaces.AF_INET6 in addrs:
                for addr in addrs[netifaces.AF_INET6]:
                    if 'addr' in addr:
                        # Remove scope id if present
                        ipv6_addr = addr['addr'].split('%')[0]
                        prefix_len = addr.get('prefixlen', 64)
                        interface_info["addresses"].append(f"{ipv6_addr}/{prefix_len}")
            
            # MAC address
            if netifaces.AF_PACKET in addrs and addrs[netifaces.AF_PACKET]:
                mac = addrs[netifaces.AF_PACKET][0].get('addr')
                if mac:
                    interface_info["mac"] = mac
            
            # Determine interface type
            if iface == 'lo' or iface.startswith('lo'):
                interface_info["type"] = "loopback"
            elif iface.startswith('eth') or iface.startswith('en'):
                interface_info["type"] = "ethernet"
            elif iface.startswith('wlan') or iface.startswith('wl') or iface.startswith('wifi'):
                interface_info["type"] = "wireless"
            elif iface.startswith('wwan') or iface.startswith('wwp'):
                interface_info["type"] = "wwan"
            elif iface.startswith('br'):
                interface_info["type"] = "bridge"
            elif iface.startswith('tun') or iface.startswith('tap'):
                interface_info["type"] = "tunnel"
            elif iface.startswith('docker') or iface.startswith('veth'):
                interface_info["type"] = "virtual"
            elif iface.startswith('bond'):
                interface_info["type"] = "bond"
            
            result_interfaces.append(interface_info)
        
        if ctx:
            await ctx.report_progress(80, 100)
            await ctx.info(f"Processed {len(result_interfaces)} interfaces")
        
        # Generate interpretation
        up_interfaces = [iface for iface in result_interfaces if iface["status"] == "up"]
        down_interfaces = [iface for iface in result_interfaces if iface["status"] == "down"]
        
        configured_interfaces = [iface for iface in result_interfaces if iface["addresses"]]
        unconfigured_interfaces = [iface for iface in result_interfaces if not iface["addresses"]]
        
        # Count by type
        interface_types = {}
        for iface in result_interfaces:
            iface_type = iface["type"]
            if iface_type not in interface_types:
                interface_types[iface_type] = 0
            interface_types[iface_type] += 1
        
        # Build interpretation
        interpretation_parts = []
        
        # Total count
        interpretation_parts.append(f"System has {len(result_interfaces)} interfaces")
        
        # Status count
        if up_interfaces:
            interpretation_parts.append(f"{len(up_interfaces)} up")
        if down_interfaces:
            interpretation_parts.append(f"{len(down_interfaces)} down")
        
        # Configuration count
        if configured_interfaces:
            interpretation_parts.append(f"{len(configured_interfaces)} with IP addresses")
        if unconfigured_interfaces:
            interpretation_parts.append(f"{len(unconfigured_interfaces)} without IP addresses")
        
        # Type summary
        type_summary = []
        for iface_type, count in interface_types.items():
            if count > 0:
                type_summary.append(f"{count} {iface_type}")
        
        if type_summary:
            interpretation_parts.append("Types: " + ", ".join(type_summary))
        
        interpretation = ": ".join(interpretation_parts)
        
        result = {
            "success": True,
            "interfaces": result_interfaces,
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Interface analysis complete: {len(result_interfaces)} interfaces found")
        
        return result
        
    except Exception as e:
        error_msg = f"Error listing network interfaces: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": "Failed to list network interfaces",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)