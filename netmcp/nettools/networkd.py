#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Networkd Config Tool

This module implements the systemd-networkd configuration reader for NetAssist.
"""
import pathlib
import json
import logging
from typing import Dict, Any
import subprocess

# Configure logging
logger = logging.getLogger("netmcp")


async def get_network_status_impl(interface: str = None, output_json=False) -> Dict[str, Any]:
    args = [
        "networkctl",
        f"--json={'short' if output_json else 'off'}",
        "status",
    ]
    if interface is not None:
        args.append(interface)

    try:
        # Run the networkctl status command and capture its output
        result = subprocess.run(
            args,
            check=True,
            text=True,
            capture_output=True,
        )
        # Return a dictionary with success set to True and message containing the output
        print(result.stdout)
        if output_json:
            return json.loads(result.stdout)

        return {"success": True, "message": result.stdout}

    except subprocess.CalledProcessError as e:
        # If an exception occurs, log it and return a dictionary with success set to False and the error message
        logger.error(
            f"Error running networkctl status for interface {interface}: {str(e.output)}"
        )
        return {
            "success": False,
            "message": str(e.output)
            + ". Consider if the interface exists or if the interface was spelled correctly. Case sensitivity matters.",
        }


async def get_network_config_file_impl(interface: str) -> str:
    network_status = await get_network_status_impl(interface, output_json=True)
    network_file = network_status.get("NetworkFile")
    network_file_dropins = network_status.get("NetworkFileDropIns")
    network_file_dropin_contents = [
        {"file": f, "contents": pathlib.Path(f).read()} for f in network_file_dropins
    ]
    network_file_contents = None

    if network_file:
        network_file_contents = {
            "file": network_file,
            "contents": pathlib.Path(network_file).read(),
        }

    return {
        "success": True,
        "networkFile": network_file_contents,
        "overrides": network_file_dropin_contents,
    }


async def set_network_static_impl(interface: str, ip_address: str, gateway: str):
    network_status = await get_network_status_impl(interface, output_json=True)
    network_file = network_status.get("NetworkFile")

    # Get drop in directory, creating if needed.
    network_file_drop_in_dir = pathlib.Path(network_file + ".d")
    network_file_drop_in_dir.mkdir(exist_ok=True)

    # Create a drop-in file 10-static with the static IP configuration if it doesn't exist.
    with (network_file_drop_in_dir / "10-static.conf").open("w") as f:
        f.write(
            f"""
[Network]
DHCP=no
Address={ip_address}/24
Gateway={gateway}
"""
        )
        logger.info("Static IP configuration created.")

        return {
            "success": True,
            "message": "Static IP configuration created. ASK USER TO IF THEY WANT TO APPLY THE CONFIGURATION. IF THEY SAY YES, RUN THE TOOL reload_network.",
        }


async def reload_network_impl():
    """
    Reload the systemd-networkd service.
    """
    try:
        logger.info("Reloading systemd-networkd service...")
        subprocess.run(["systemctl", "restart", "systemd-networkd"], check=True)
        logger.info("Systemd-networkd service reloaded.")
        return {
            "success": True,
            "message": "Network reloaded. Confirm applied configuration with get_network_status.",
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload systemd-networkd: {e}")
        return {"success": False, "message": f"Failed to reload systemd-networkd: {e}"}
