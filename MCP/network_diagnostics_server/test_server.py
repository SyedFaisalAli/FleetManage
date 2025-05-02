from fastmcp import Client
import asyncio
import os
import sys
import json
from pathlib import Path
from fastmcp.client.transports import (
    SSETransport,
    PythonStdioTransport,
    FastMCPTransport
)

def print_json(data, title=None):
    """Print JSON data in a readable format with an optional title."""
    if title:
        print(f"\n=== {title} ===")
    # print(json.dumps(str(data), indent=2))
    print("=" * 50)

async def test_ping(client, host="8.8.8.8", count=4):
    """Test the run_ping tool with the given host and count."""
    print(f"\nTesting ping to {host} with count {count}...")
    
    try:
        result = await client.call_tool("run_ping", {"host": host, "count": count})
        result = json.loads(result[0].text)
        print_json(result, "Ping Results")
        
        # Print a more user-friendly summary
        if result.get("success", False):
            stats = result.get("results", {})
            print(f"Summary: {stats.get('received', 0)}/{stats.get('sent', 0)} packets received, "
                  f"{stats.get('loss_percentage', 'N/A')}% loss")
            print(f"RTT (min/avg/max): {stats.get('min_rtt', 'N/A')}/{stats.get('avg_rtt', 'N/A')}/{stats.get('max_rtt', 'N/A')}")
            print(f"Interpretation: {result.get('interpretation', 'No interpretation available')}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing ping: {e}")

async def test_ip_command(client, command="addr", interface=""):
    """Test the run_ip_command tool with the given command and interface."""
    print(f"\nTesting ip {command} for {interface or 'all interfaces'}...")
    
    try:
        params = {"command": command}
        if interface:
            params["interface"] = interface
            
        result = await client.call_tool("run_ip_command", params)
        result = json.loads(result[0].text)
        print_json(result, f"IP {command.upper()} Results")
        
        # Print a more user-friendly summary
        if result.get("success", False):
            print(f"Command: {result.get('command', '')}")
            
            # Print parsed data summary based on command
            parsed_data = result.get("parsed_data", [])
            if command == "addr":
                print(f"Found {len(parsed_data)} interfaces with IP addresses:")
                for iface in parsed_data:
                    addr_count = len(iface.get("addresses", []))
                    print(f"  - {iface.get('name', 'unknown')}: {addr_count} address(es)")
            
            elif command == "link":
                print(f"Found {len(parsed_data)} interfaces:")
                for iface in parsed_data:
                    state = iface.get("state", "UNKNOWN")
                    mac = iface.get("mac", "Unknown MAC")
                    print(f"  - {iface.get('name', 'unknown')}: {state}, MAC: {mac}")
            
            elif command == "route":
                default_routes = [r for r in parsed_data if r.get("type") == "default"]
                other_routes = [r for r in parsed_data if r.get("type") != "default"]
                
                if default_routes:
                    print("Default routes:")
                    for route in default_routes:
                        print(f"  - via {route.get('via', 'unknown')} dev {route.get('dev', 'unknown')}")
                
                if other_routes:
                    print(f"Other routes ({len(other_routes)}):")
                    for i, route in enumerate(other_routes[:3]):  # Show only first 3
                        print(f"  - {route.get('dest', 'unknown')} dev {route.get('dev', 'unknown')}")
                    if len(other_routes) > 3:
                        print(f"  - ... and {len(other_routes) - 3} more")
            
            print(f"Interpretation: {result.get('interpretation', 'No interpretation available')}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing ip command: {e}")

async def test_diagnose_connectivity(client, target="8.8.8.8"):
    """Test the diagnose_connectivity tool with the given target."""
    print(f"\nTesting connectivity diagnosis to {target}...")
    
    try:
        result = await client.call_tool("diagnose_connectivity", {"target": target})
        result = json.loads(result[0].text)
        print_json(result, "Connectivity Diagnosis Results")
        
        # Print a more user-friendly summary
        if result.get("success", False):
            tests = result.get("tests", [])
            issues = result.get("issues", [])
            
            print(f"Ran {len(tests)} connectivity tests:")
            
            # Count passes and failures
            passes = sum(1 for test in tests if test.get("result") == "PASS")
            failures = sum(1 for test in tests if test.get("result") == "FAIL")
            
            # Print test results
            for test in tests:
                result_str = test.get("result", "UNKNOWN")
                result_symbol = "✅" if result_str == "PASS" else "❌" if result_str == "FAIL" else "❓"
                print(f"  {result_symbol} {test.get('name', 'Unknown test')}: {test.get('details', 'No details')}")
            
            # Print summary
            print(f"\nSummary: {passes} passed, {failures} failed")
            
            if issues:
                print(f"Issues detected: {', '.join(issues)}")
            else:
                print("No issues detected")
            
            print(f"Interpretation: {result.get('interpretation', 'No interpretation available')}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing connectivity diagnosis: {e}")

async def test_read_networkd_config(client, interface=""):
    """Test the read_networkd_config tool with the given interface."""
    print(f"\nTesting read_networkd_config for {interface or 'all interfaces'}...")
    
    try:
        params = {}
        if interface:
            params["interface"] = interface
            
        result = await client.call_tool("read_networkd_config", params)
        result = json.loads(result[0].text)
        print_json(result, "Networkd Config Results")
        
        # Print a more user-friendly summary
        if result.get("success", False):
            config_files = result.get("config_files", [])
            print(f"Found {len(config_files)} configuration files:")
            
            for i, config in enumerate(config_files):
                interface_name = config.get("interface", "unknown")
                path = config.get("path", "unknown")
                is_orphaned = config.get("is_orphaned", False)
                
                if is_orphaned:
                    print(f"  {i+1}. [ORPHANED DROP-INS] {path} for interface {interface_name}")
                else:
                    print(f"  {i+1}. {os.path.basename(path)} for interface {interface_name}")
                
                # Show drop-ins if any
                dropins = config.get("dropins", [])
                if dropins:
                    print(f"     - With {len(dropins)} drop-in files:")
                    for dropin in dropins[:3]:  # Show only first 3
                        print(f"       * {dropin.get('name', 'unknown')}")
                    if len(dropins) > 3:
                        print(f"       * ... and {len(dropins) - 3} more")
                
                # Show network configuration if available
                sections = config.get("sections", {})
                if "Network" in sections:
                    network = sections["Network"]
                    if "DHCP" in network:
                        print(f"     - DHCP: {network['DHCP']}")
                    if "Address" in network:
                        print(f"     - Static Address: {network['Address']}")
            
            print(f"Interpretation: {result.get('interpretation', 'No interpretation available')}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing read_networkd_config: {e}")

async def test_netstat(client, options="tuln"):
    """Test the run_netstat tool with the given options."""
    print(f"\nTesting netstat with options '{options}'...")
    
    try:
        result = await client.call_tool("run_netstat", {"options": options})
        result = json.loads(result[0].text)
        print_json(result, "Netstat Results")
        
        # Print a more user-friendly summary
        if result.get("success", False):
            print(f"Command: {result.get('command', '')}")
            
            # Print connection summary
            connections = result.get("connections", [])
            
            # Count by protocol and state
            tcp_listen = sum(1 for c in connections if c.get("proto") == "tcp" and c.get("state") == "LISTEN")
            tcp_established = sum(1 for c in connections if c.get("proto") == "tcp" and c.get("state") == "ESTABLISHED")
            udp = sum(1 for c in connections if c.get("proto") == "udp")
            
            print(f"Found {len(connections)} connections:")
            print(f"  - TCP listening: {tcp_listen}")
            print(f"  - TCP established: {tcp_established}")
            print(f"  - UDP: {udp}")
            
            # Print services if available
            services = {}
            for conn in connections:
                if "service" in conn:
                    service = conn["service"]
                    if service not in services:
                        services[service] = 0
                    services[service] += 1
            
            if services:
                print("Services detected:")
                for service, count in services.items():
                    print(f"  - {service}: {count} connection(s)")
            
            print(f"Interpretation: {result.get('interpretation', 'No interpretation available')}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"Error testing netstat: {e}")

async def testclient():
    # Get the absolute path to the server.py file
    current_dir = Path(__file__).parent
    server_path = current_dir / "server.py"
    
    # Connect to a Python script using stdio (useful for local tools)
    async with Client(PythonStdioTransport(str(server_path))) as client:
        # List available tools
        print(f"\n=== TOOLS ===")
        tools = await client.list_tools()
        for tool in tools:
            print(f"{tool.name} - {tool.description}")
        
        # List available resources
        print(f"\n=== RESOURCES ===")
        resources = await client.list_resources()
        for resource in resources:
            print(resource.name, tool.description)

        # Test the network interfaces tool
        result = await client.call_tool("list_network_interfaces")
        print_json(result, "Network Interfaces")
        
        # Test the ping tool with Google's DNS
        await test_ping(client, "8.8.8.8", 4)
        
        # Test the ping tool with a local address
        await test_ping(client, "127.0.0.1", 2)
        
        # Test the ping tool with an invalid host (should fail gracefully)
        await test_ping(client, "invalid.host.example", 1)
        
        # Test the ip addr command for all interfaces
        await test_ip_command(client, "addr")
        
        # Test the ip link command for all interfaces
        await test_ip_command(client, "link")
        
        # Test the ip route command for all interfaces
        await test_ip_command(client, "route")
        
        # Get a list of interfaces to test with a specific interface
        try:
            import netifaces
            interfaces = netifaces.interfaces()
            if interfaces:
                # Test with the first interface
                test_interface = interfaces[0]
                print(f"\nTesting with specific interface: {test_interface}")
                
                # Test ip addr for specific interface
                await test_ip_command(client, "addr", test_interface)
                
                # Test ip link for specific interface
                await test_ip_command(client, "link", test_interface)
                
                # Test ip route for specific interface
                await test_ip_command(client, "route", test_interface)
        except ImportError:
            print("\nCould not import netifaces to get interface list")
        except Exception as e:
            print(f"\nError testing with specific interface: {e}")
            
        # Test the netstat tool with different options
        
        # Test listening TCP and UDP sockets (default)
        await test_netstat(client, "tuln")
        
        # Test only TCP listening sockets
        await test_netstat(client, "tln")
        
        # Test all TCP connections (listening and established)
        await test_netstat(client, "tn")
        
        # Test reading networkd configuration
        
        # Test for all interfaces
        await test_read_networkd_config(client)
        
        # If we have interfaces, test with a specific interface
        if 'interfaces' in locals() and interfaces:
            # Test with the first interface
            await test_read_networkd_config(client, interfaces[0])
        
        # Test connectivity diagnosis
        
        # Test with Google's DNS
        await test_diagnose_connectivity(client, "8.8.8.8")
        
        # Test with Cloudflare's DNS as an alternative
        await test_diagnose_connectivity(client, "1.1.1.1")

if __name__ == "__main__":
    asyncio.run(testclient())