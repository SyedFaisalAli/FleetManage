# NetAssist

   [ [Report](https://github.com/SyedFaisalAli/NetAssist/blob/1573200ea6de4d9a29c4ceae7bfb9350696bf23f/report.pdf) ] [ [Video](https://youtu.be/Bo1_-jrvnLw) ]

NetAssist is a local agent to assist with network troubleshooting, focusing on systemd-networkd configurations within. It uses a client-server architecture with the Model Context Protocol (MCP) for communication, intended to interface with an Small Language Model (SLM) running locally on the same device. A built-in web console is provided for user-interaction.

For more details on the architecture, see report.pdf.

## Requirements

- Python 3.8 or higher
- Ollama or any other compatible server that provides an OpenAI-compatible API endpoint

## Setup

### 1. Clone the repo

Clone the repository and navigate into it:
```bash
git clone https://github.com/SyedFaisalAli/NetAssist
cd NetAssist
```

### 2. Set up Ollama

The Agent uses Ollama for language model inference. Follow these steps to set it up:
```bash
# Pull Ollama docker image
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Start Ollama with a model of your choice (e.g., qwen3:1.7b)
docker exec ollama ollama pull qwen3:1.7b
```

### 3. Install and run MCP and Agent

```bash
# Install through pipx
pipx install .
```

### 3. Run the Network Troubleshooting Client

First, make sure the MCP server is running:

```bash
# Run the agent
netassist
```
