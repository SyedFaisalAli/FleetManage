#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Netstat Tool

This module implements the netstat diagnostic tool for the Fleet Management system.
"""

import logging
import psutil
import socket
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("network_diagnostics_server")

async def run_netstat_impl(options: str = "tuln", ctx = None) -> Dict[str, Any]:
    """
    Show network connections and statistics using psutil.
    
    Args:
        options: Netstat options (e.g., 'tuln' for TCP/UDP listening sockets)
        ctx: The MCP context
        
    Returns:
        Dict containing the network connections and interpretation
    """
    
    logger.info(f"Getting network connections with options '{options}'")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info(f"Getting network connections with options '{options}'")
    
    try:
        # Parse options
        show_tcp = 't' in options.lower()
        show_udp = 'u' in options.lower()
        show_listening = 'l' in options.lower()
        show_numeric = 'n' in options.lower()
        show_all = not (show_tcp or show_udp)  # If neither t nor u specified, show both
        
        if ctx:
            await ctx.report_progress(20, 100)
            await ctx.info("Retrieving network connections")
        
        # Get connections using psutil
        connections = []
        
        # Get TCP connections if requested
        if show_tcp or show_all:
            tcp_connections = psutil.net_connections(kind='tcp')
            for conn in tcp_connections:
                # Skip non-listening connections if only listening requested
                if show_listening and conn.status != 'LISTEN':
                    continue
                
                # Format addresses
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "*:*"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
                
                # Resolve hostnames if not numeric
                if not show_numeric:
                    try:
                        if conn.laddr and conn.laddr.ip != "0.0.0.0" and conn.laddr.ip != "::":
                            laddr = f"{socket.getfqdn(conn.laddr.ip)}:{conn.laddr.port}"
                    except (socket.error, socket.herror):
                        pass
                    
                    try:
                        if conn.raddr:
                            raddr = f"{socket.getfqdn(conn.raddr.ip)}:{conn.raddr.port}"
                    except (socket.error, socket.herror):
                        pass
                
                connections.append({
                    "proto": "tcp",
                    "local_address": laddr,
                    "foreign_address": raddr,
                    "state": conn.status,
                    "pid": conn.pid
                })
        
        # Get UDP connections if requested
        if show_udp or show_all:
            udp_connections = psutil.net_connections(kind='udp')
            for conn in udp_connections:
                # Format addresses
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "*:*"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
                
                # Resolve hostnames if not numeric
                if not show_numeric:
                    try:
                        if conn.laddr and conn.laddr.ip != "0.0.0.0" and conn.laddr.ip != "::":
                            laddr = f"{socket.getfqdn(conn.laddr.ip)}:{conn.laddr.port}"
                    except (socket.error, socket.herror):
                        pass
                    
                    try:
                        if conn.raddr:
                            raddr = f"{socket.getfqdn(conn.raddr.ip)}:{conn.raddr.port}"
                    except (socket.error, socket.herror):
                        pass
                
                connections.append({
                    "proto": "udp",
                    "local_address": laddr,
                    "foreign_address": raddr,
                    "state": conn.status,
                    "pid": conn.pid
                })
        
        if ctx:
            await ctx.report_progress(60, 100)
            await ctx.info(f"Processing {len(connections)} connections")
        
        # Identify common services by port
        common_ports = {
            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            25: "SMTP",
            110: "POP3",
            143: "IMAP",
            53: "DNS",
            21: "FTP",
            23: "Telnet",
            3306: "MySQL",
            5432: "PostgreSQL",
            27017: "MongoDB",
            6379: "Redis",
            11211: "Memcached",
            8080: "HTTP-ALT",
            8443: "HTTPS-ALT",
            631: "CUPS",
            3389: "RDP"
        }
        
        # Add service names to connections
        for conn in connections:
            if ":" in conn["local_address"]:
                try:
                    port = int(conn["local_address"].split(":")[-1])
                    if port in common_ports:
                        conn["service"] = common_ports[port]
                except ValueError:
                    pass
        
        # Generate interpretation
        listening_tcp = [c for c in connections if c["proto"] == "tcp" and c["state"] == "LISTEN"]
        listening_udp = [c for c in connections if c["proto"] == "udp"]
        established = [c for c in connections if c["state"] == "ESTABLISHED"]
        
        interpretation_parts = []
        
        if show_listening or not established:
            if listening_tcp:
                services = []
                for conn in listening_tcp:
                    if "service" in conn:
                        services.append(f"{conn['service']} (port {conn['local_address'].split(':')[-1]})")
                    else:
                        services.append(f"port {conn['local_address'].split(':')[-1]}")
                
                if services:
                    interpretation_parts.append(f"System has {len(listening_tcp)} listening TCP services: {', '.join(services[:5])}")
                    if len(services) > 5:
                        interpretation_parts[-1] += f" and {len(services) - 5} more"
            
            if listening_udp:
                udp_services = []
                for conn in listening_udp:
                    if "service" in conn:
                        udp_services.append(f"{conn['service']} (port {conn['local_address'].split(':')[-1]})")
                    else:
                        udp_services.append(f"port {conn['local_address'].split(':')[-1]}")
                
                if udp_services:
                    interpretation_parts.append(f"System has {len(listening_udp)} UDP services: {', '.join(udp_services[:5])}")
                    if len(udp_services) > 5:
                        interpretation_parts[-1] += f" and {len(udp_services) - 5} more"
        
        if established and not show_listening:
            interpretation_parts.append(f"System has {len(established)} established connections")
        
        if not interpretation_parts:
            interpretation = "No network connections found matching the specified criteria"
        else:
            interpretation = ". ".join(interpretation_parts)
        
        result = {
            "success": True,
            "command": f"netstat -{options}",
            "connections": connections,
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Netstat complete: found {len(connections)} connections")
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting network connections: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": "Failed to get network connections",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)