# Network Diagnostics MCP Server

This is a Model Context Protocol (MCP) server that provides network diagnostic tools for the Nvidia Jetson Orin Nano, focusing on systemd-networkd.

## Features

- Run basic network diagnostic commands (ping, ifconfig/ip, netstat)
- Read and interpret systemd-networkd configuration files
- Check service status
- Diagnose common network configuration issues

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the package:

```bash
pip install -e .
```

## Usage

### Running the Server

To run the server:

```bash
network-diagnostics-mcp
```

Or directly:

```bash
python -m network_diagnostics_server.server
```

### MCP Configuration

To use this server with an MCP client, add the following configuration to your MCP settings file:

```json
{
  "mcpServers": {
    "network-diagnostics": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "network_diagnostics_server.server"],
      "disabled": false
    }
  }
}
```

## Available Tools

The server provides the following tools:

1. `run_ping`: Ping a host and interpret the results
2. `run_ip_command`: Run ip commands (addr, link, route) with interpretation
3. `run_netstat`: Show network connections and statistics
4. `read_networkd_config`: Read and parse systemd-networkd configuration files
5. `list_network_interfaces`: List all network interfaces with their status
6. `check_service_status`: Check the status of systemd-networkd service
7. `diagnose_connectivity`: Run a series of tests to diagnose connectivity issues
8. `interpret_ip_config`: Provide a human-readable interpretation of IP configuration

## Testing the MCP Server

A test script is provided to demonstrate how to use the MCP server from Python code:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the test script
./test_mcp_server.py
```

The test script demonstrates:
1. Listing network interfaces
2. Checking systemd-networkd service status
3. Running a ping test
4. Diagnosing connectivity

## Example Tool Usage

### Diagnosing Connectivity

```python
result = await client.call_tool("network-diagnostics", "diagnose_connectivity", {
    "target": "8.8.8.8"
})
print(result.content[0].text)
```

### Checking Network Interfaces

```python
result = await client.call_tool("network-diagnostics", "list_network_interfaces", {})
print(result.content[0].text)
```

For more examples, see the `test_mcp_server.py` script.

## Requirements

- Python 3.8 or higher
- MCP SDK
- psutil
- netifaces2