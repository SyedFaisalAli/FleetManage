#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Connectivity Diagnostics Tool

This module implements the connectivity diagnostics tool for the Fleet Management system.
"""

import logging
import subprocess
import socket
import netifaces
import psutil
from typing import Dict, List, Any, Optional
from .utils import get_default_gateway

# Configure logging
logger = logging.getLogger("network_diagnostics_server")

async def diagnose_connectivity_impl(target: str = "8.8.8.8", ctx = None) -> Dict[str, Any]:
    """
    Run a series of tests to diagnose connectivity issues.
    
    Args:
        target: Target host to test connectivity to
        ctx: The MCP context
        
    Returns:
        Dict containing the diagnostic results
    """
    
    logger.info(f"Diagnosing connectivity to {target}")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info(f"Diagnosing connectivity to {target}")
    
    try:
        tests = []
        issues = []
        
        # Test 1: Check if any network interfaces are up
        if ctx:
            await ctx.report_progress(10, 100)
            await ctx.info("Checking network interface status")
        
        net_stats = psutil.net_if_stats()
        up_interfaces = [iface for iface, stats in net_stats.items() if stats.isup]
        
        if up_interfaces:
            tests.append({
                "name": "Interface status",
                "result": "PASS",
                "details": f"Found {len(up_interfaces)} active network interfaces: {', '.join(up_interfaces[:3])}"
                           + (f" and {len(up_interfaces) - 3} more" if len(up_interfaces) > 3 else "")
            })
        else:
            tests.append({
                "name": "Interface status",
                "result": "FAIL",
                "details": "No active network interfaces found"
            })
            issues.append("No active network interfaces")
        
        # Test 2: Check if we have IP addresses
        if ctx:
            await ctx.report_progress(20, 100)
            await ctx.info("Checking IP configuration")
        
        ip_addresses = []
        for iface in up_interfaces:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if 'addr' in addr and addr['addr'] != '127.0.0.1':
                        ip_addresses.append(addr['addr'])
        
        if ip_addresses:
            tests.append({
                "name": "IP configuration",
                "result": "PASS",
                "details": f"Found {len(ip_addresses)} IP addresses: {', '.join(ip_addresses[:3])}"
                           + (f" and {len(ip_addresses) - 3} more" if len(ip_addresses) > 3 else "")
            })
        else:
            tests.append({
                "name": "IP configuration",
                "result": "FAIL",
                "details": "No IP addresses found (other than loopback)"
            })
            issues.append("No IP addresses configured")
        
        # Test 3: Check if we can reach the default gateway
        if ctx:
            await ctx.report_progress(30, 100)
            await ctx.info("Checking default gateway connectivity")
        
        gateway_reachable = False
        gateway_ip = None
        
        try:
            default_gw_ip = get_default_gateway()
            if default_gw_ip:
                gateway_ip = default_gw_ip
                ping_cmd = ["ping", "-c", "1", "-W", "2", default_gw_ip]
                ping_process = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=5)
                gateway_reachable = ping_process.returncode == 0
        except Exception as e:
            logger.warning(f"Error checking gateway: {e}")
        
        if gateway_reachable:
            tests.append({
                "name": "Gateway connectivity",
                "result": "PASS",
                "details": f"Can reach default gateway ({gateway_ip})"
            })
        elif gateway_ip:
            tests.append({
                "name": "Gateway connectivity",
                "result": "FAIL",
                "details": f"Cannot reach default gateway ({gateway_ip})"
            })
            issues.append("Cannot reach default gateway")
        else:
            tests.append({
                "name": "Gateway connectivity",
                "result": "FAIL",
                "details": "No default gateway found"
            })
            issues.append("No default gateway configured")
        
        # Test 4: Check DNS resolution
        if ctx:
            await ctx.report_progress(50, 100)
            await ctx.info("Checking DNS resolution")
        
        dns_working = False
        dns_error = None
        
        try:
            # Try to resolve a well-known domain
            socket.gethostbyname("www.google.com")
            dns_working = True
        except socket.gaierror as e:
            dns_error = str(e)
        except Exception as e:
            dns_error = str(e)
        
        if dns_working:
            tests.append({
                "name": "DNS resolution",
                "result": "PASS",
                "details": "DNS resolution is working correctly"
            })
        else:
            tests.append({
                "name": "DNS resolution",
                "result": "FAIL",
                "details": f"DNS resolution failed: {dns_error}"
            })
            issues.append("DNS resolution not working")
        
        # Test 5: Check connectivity to target
        if ctx:
            await ctx.report_progress(70, 100)
            await ctx.info(f"Checking connectivity to target {target}")
        
        target_reachable = False
        target_error = None
        
        try:
            # Try to ping the target
            ping_cmd = ["ping", "-c", "3", "-W", "2", target]
            ping_process = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=10)
            target_reachable = ping_process.returncode == 0
            
            if not target_reachable:
                target_error = ping_process.stderr.strip() or "Ping failed"
        except Exception as e:
            target_error = str(e)
        
        if target_reachable:
            tests.append({
                "name": "Target connectivity",
                "result": "PASS",
                "details": f"Can reach target {target}"
            })
        else:
            tests.append({
                "name": "Target connectivity",
                "result": "FAIL",
                "details": f"Cannot reach target {target}: {target_error}"
            })
            issues.append(f"Cannot reach target {target}")
        
        # Generate interpretation
        if not issues:
            interpretation = "Network connectivity is working correctly with no issues detected"
        else:
            interpretation = f"Network connectivity issues detected: {', '.join(issues)}"
            
            # Add troubleshooting suggestions
            suggestions = []
            
            if "No active network interfaces" in issues:
                suggestions.append("Check if network cables are connected or wireless is enabled")
            
            if "No IP addresses configured" in issues:
                suggestions.append("Check DHCP service or configure static IP")
            
            if "Cannot reach default gateway" in issues:
                suggestions.append("Check physical connectivity to router/switch")
            
            if "DNS resolution not working" in issues:
                suggestions.append("Check DNS server settings or try using public DNS servers (8.8.8.8, 1.1.1.1)")
            
            if f"Cannot reach target {target}" in issues and "DNS resolution not working" not in issues:
                suggestions.append("Check firewall settings or if the target host is online")
            
            if suggestions:
                interpretation += ". Suggestions: " + "; ".join(suggestions)
        
        result = {
            "success": True,
            "target": target,
            "tests": tests,
            "issues": issues,
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Diagnosis complete: {interpretation}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error diagnosing connectivity: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": "Failed to diagnose connectivity",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)