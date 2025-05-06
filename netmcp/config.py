import json
import pathlib
import logging

log = logging.getLogger('netmcp')

CONFIG = {}

def load_config(config_path: str):
    """
    Load the configuration from a JSON file.
    """
    global CONFIG

    try:
        CONFIG = json.load(pathlib.Path(config_path).open("r"))
    except FileNotFoundError:
        log.warning(f"Config file {config_path} not found, using default config")
        raise
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse config file {config_path}: {e}")
        raise