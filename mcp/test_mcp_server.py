#!/usr/bin/env python3
"""
Test script for the Network Diagnostics MCP Server

This script demonstrates how to use the MCP server from Python code.
"""

import asyncio
import json
from mcp.client import Client

async def test_network_diagnostics():
    """Test the network diagnostics MCP server"""
    # Create an MCP client
    client = Client()
    
    # Connect to the MCP server
    await client.connect()
    
    try:
        print("Testing Network Diagnostics MCP Server\n")
        
        # Test 1: List network interfaces
        print("Test 1: List network interfaces")
        result = await client.call_tool("network-diagnostics", "list_network_interfaces", {})
        print(result.content[0].text)
        print("-" * 50)
        
        # Test 2: Check systemd-networkd service status
        print("Test 2: Check systemd-networkd service status")
        result = await client.call_tool("network-diagnostics", "check_service_status", {})
        print(result.content[0].text)
        print("-" * 50)
        
        # Test 3: Run a ping test
        print("Test 3: Run a ping test")
        result = await client.call_tool("network-diagnostics", "run_ping", {
            "host": "8.8.8.8",
            "count": 3
        })
        print(result.content[0].text)
        print("-" * 50)
        
        # Test 4: Diagnose connectivity
        print("Test 4: Diagnose connectivity")
        result = await client.call_tool("network-diagnostics", "diagnose_connectivity", {
            "target": "8.8.8.8"
        })
        print(result.content[0].text)
        print("-" * 50)
        
    finally:
        # Disconnect from the MCP server
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_network_diagnostics())