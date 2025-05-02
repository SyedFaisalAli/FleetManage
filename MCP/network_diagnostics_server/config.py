import json
import os
import pathlib

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/etc/MCP/network/config.json")

try:
    CONFIG = json.load(pathlib.Path(CONFIG_PATH).open("r"))
except FileNotFoundError:
    CONFIG = {}