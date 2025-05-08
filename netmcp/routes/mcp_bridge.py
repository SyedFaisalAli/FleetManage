import argparse
import traceback
import json
import logging
import datetime
import netifaces
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastmcp import Client as FastMCPClient
from fastmcp.tools import Tool
from fastmcp.exceptions import ClientError
from qwen_agent.llm import get_chat_model
from qwen_agent.utils.output_beautify import typewriter_print
from .mcp import mcp
from ..config import get_config
log = logging.getLogger('netmcp')

SSE_URL = "http://localhost:8000/sse"
DEFAULT_MODEL_CONFIG = {
    "model": "qwen3:1.7b",
    "model_server": "http://localhost:11434/v1",
    "generate_cfg": {
        "temperature": 0.6,
        "top_p": 0.95,
    }
}

interface_list =  [iface for iface in netifaces.interfaces() if iface != 'lo']
SYSTEM_PROMPT = f"""
You are a network troubleshooting assistant for the current device and its network configuration.
Your task is to help users troubleshoot network issues on their devices. Run the necessary tools to diagnose and resolve network issues or requests.
If there is any missing information, prompt the user for more information.

These are the available interfaces: {", ".join(interface_list)}
"""

mcp_bridge_router = APIRouter()

def fastmcp_tool_to_openai_schema(tool: Tool) -> dict:
    fields = tool.model_dump()
    tool_schema = getattr(tool, "inputSchema", {"type": "object", "properties": {}, "required": []})

    return {
        "type": "function",
        "function": {
            "name": fields["name"],
            "description": fields["description"],
            "parameters": tool_schema
        }
    }

def init_agent_service():
    return get_chat_model(get_config("modelcfg", DEFAULT_MODEL_CONFIG))

@mcp_bridge_router.websocket_route("/ws")
async def mcp_bridge(websocket: WebSocket):
    try:
        await websocket.accept()
        llm = init_agent_service()
        client = FastMCPClient(mcp)
        await websocket.send_json({"type": "status", "content": "Connected!"})
    except Exception as e:
        traceback.format_exc()
        await websocket.send_json({"type": "error", "content": str(e)})
        return

    async with client:
        function_list = [fastmcp_tool_to_openai_schema(tool) for tool in await client.list_tools()]
        responses = []
        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT
        }]
        while True:
            try:
                data = await websocket.receive_text()
                if not data:
                    continue

                data = json.loads(data)
                messages.append(data)
                finished = False

                while not finished:
                    isodate = datetime.datetime.now().isoformat()
                    for responses in llm.chat(
                        messages=messages,
                        functions=function_list,
                        stream=True,
                    ):
                        for msg in responses:
                            await websocket.send_json({
                                "type": "response",
                                "role": msg["role"],
                                "timestamp": isodate,
                                "content": msg["content"]
                            })
                    messages.extend(responses)

                    last_response = messages[-1]
                    if last_response.get('function_call', None):
                        isodate = datetime.datetime.now().isoformat()
                        function_name = last_response['function_call']['name']
                        function_args = json.loads(last_response['function_call']['arguments'])
                        function_response = await client.call_tool(function_name, function_args)
                        print(function_response)
                        function_message = {
                            "type": "function",
                            "role": "function",
                            "functionName": function_name,
                            "timestamp": isodate,
                            "content": str(function_response[0].text)
                        }
                        await websocket.send_json(function_message)
                        messages.append(function_message)
                    else:
                        # If no functions are being called, we assume that the assistant is either done or is waiting for user input.
                        finished = True
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid formatted response."})
            except ClientError:
                traceback.print_exc()
                await websocket.send_json({"type": "error", "content": f"Unable to execute function {function_name}."})
            except Exception as e:
                traceback.print_exc()
                await websocket.send_json({"type": "error", "content": str(e)})


def main(args):
    bot = init_agent_service()

    messages = [{"role": "user", "content": args.issue}]
    response_plain_text = ""
    response = []
    for response in bot.run(messages=messages):
        response_plain_text = typewriter_print(response, response_plain_text)
    messages.extend(response)
    print()  # Print a newline after the streaming is complete

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network troubleshooting assistant.")
    parser.add_argument("issue", type=str, help="Enter your troubleshooting issue.")
    args = parser.parse_args()

    main(args)