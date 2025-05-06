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
        
        await ctx.report_progress(100, 100)
        return {
            "success": True,
            "message": "Successfully listed network interfaces",
            "interfaces": [iface for iface in interfaces]
        }
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