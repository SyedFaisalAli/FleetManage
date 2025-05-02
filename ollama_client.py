import argparse
import logging
from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print

log = logging.getLogger("Network Troubleshooting Assistant")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

SSE_URL = "http://localhost:8888/sse"


def init_agent_service():
    llm_cfg = {
        "model": "qwen3:1.7b",
        "model_server": "http://localhost:11434/v1",
        "generate_cfg": {
            "temperature": 0.6,
            "top_p": 0.95,
        }
        # "temperature": 0.3,
        # "max_tokens": 512,
        # "top_p": 0.95,
        # "frequency_penalty": 0,
        # "presence_penalty": 0,
        # "stop_sequence": None,
    }
    tools = [{
        "mcpServers": {
            "network": {
                "url": SSE_URL,
            }
        }
    }]
    bot = Assistant(
        llm=llm_cfg,
        function_list=tools,
        name="Network Troubleshooting Assistant",
        description="A network troubleshooting assistant for systemd-networkd.",
        system_message="You are a network troubleshooting assistant. You can help users diagnose and suggest network fixes related to systemd-networkd.",
    )
    
    return bot

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