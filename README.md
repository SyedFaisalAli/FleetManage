# Network Troubleshooting LLM Agent for Nvidia Jetson Orin Nano

This project implements a local LLM agent that runs on the Nvidia Jetson Orin Nano to assist with network troubleshooting, focusing on systemd-networkd.

## Architecture

The solution uses a client-server architecture with the Model Context Protocol (MCP):

1. **LLM Agent (Docker Container)**
   - Runs the quantized Sheared-LLaMA-2.7B-ShareGPT model using NanoLLM
   - Communicates with the MCP server to access network diagnostics
   - Provides natural language interface for troubleshooting

2. **Python MCP Server (Host)**
   - Runs on the host system with access to network configuration
   - Exposes network diagnostic tools via MCP protocol
   - Executes commands and interprets results
   - Reads systemd-networkd configuration files
   - Checks service status

## Setup Instructions

### 1. Install the MCP Server

```bash
# Navigate to the MCP directory
cd MCP

# Run the installation script
./install.sh
```

This will:
- Create a Python virtual environment
- Install the required dependencies
- Install the MCP server in development mode

### 2. Configure the MCP Server

The MCP server configuration is in `MCP/mcp_config.json`. You can modify this file if needed, for example, to change the path to the Python interpreter.

### 3. Run the Network Troubleshooting Client

First, make sure the MCP server is running:

```bash
cd MCP
source venv/bin/activate
network-diagnostics-mcp &
```

Then, run the network troubleshooting client using NVIDIA's jetson-containers:

```bash
cd ..
jetson-containers run --volume $PWD:/workdir $(autotag nano_llm) python3 /workdir/network_client.py
```

This command:
- Uses NVIDIA's jetson-containers to run the client in a container
- Mounts the current directory to /workdir in the container
- Uses the nano_llm container image
- Runs the network_client.py script from the mounted directory

## Available Network Diagnostic Tools

The MCP server provides the following tools:

1. `run_ping`: Ping a host and interpret the results
2. `run_ip_command`: Run ip commands (addr, link, route) with interpretation
3. `run_netstat`: Show network connections and statistics
4. `read_networkd_config`: Read and parse systemd-networkd configuration files
5. `list_network_interfaces`: List all network interfaces with their status
6. `check_service_status`: Check the status of systemd-networkd service
7. `diagnose_connectivity`: Run a series of tests to diagnose connectivity issues
8. `interpret_ip_config`: Provide a human-readable interpretation of IP configuration

## Example Usage

Once the client is running, you can ask questions like:

- "Can you check if my network interfaces are configured correctly?"
- "Is systemd-networkd running properly?"
- "I can't connect to the internet, can you help diagnose the issue?"
- "What's the IP configuration of eth0?"
- "Can you ping 8.8.8.8 and tell me if it works?"

## Project Structure

```
FleetManage/
├── client.py                  # Original NanoLLM client
├── network_client.py          # Network troubleshooting client
├── README.md                  # This file
└── MCP/                       # MCP server directory
    ├── install.sh             # Installation script
    ├── mcp_config.json        # MCP server configuration
    ├── README.md              # MCP server documentation
    ├── requirements.txt       # Python dependencies
    ├── setup.py               # Package setup script
    └── netmcp/  # MCP server implementation
        ├── __init__.py
        ├── server.py          # Main server file
        ├── network_tools.py   # Network diagnostic tools
        └── systemd_tools.py   # Systemd-related tools
```

## Requirements

- Nvidia Jetson Orin Nano
- Python 3.8 or higher
- Docker (optional, for running the LLM in a container)
- NanoLLM library
- MCP SDK
