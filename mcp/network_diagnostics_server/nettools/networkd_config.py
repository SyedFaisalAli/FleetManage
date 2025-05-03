#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Networkd Config Tool

This module implements the systemd-networkd configuration reader for the Fleet Management system.
"""

import logging
import os
import glob
import configparser
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("network_diagnostics_server")

async def read_networkd_config_impl(interface: str = "", ctx = None) -> Dict[str, Any]:
    """
    Read and parse systemd-networkd configuration files, including drop-in files.
    
    Args:
        interface: Optional interface name to filter results
        ctx: The MCP context
        
    Returns:
        Dict containing the parsed configuration
    """
    
    logger.info(f"Reading networkd config for interface '{interface or 'all'}'")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info(f"Reading networkd config for {interface or 'all interfaces'}")
    
    try:
        # Define paths where systemd-networkd config files are stored
        config_paths = [
            "/etc/systemd/network/*.network",
            "/lib/systemd/network/*.network",
            "/run/systemd/network/*.network"
        ]
        
        # Define paths for drop-in directories
        dropin_paths = [
            "/etc/systemd/network/*.network.d/*.conf",
            "/lib/systemd/network/*.network.d/*.conf",
            "/run/systemd/network/*.network.d/*.conf"
        ]
        
        if ctx:
            await ctx.report_progress(10, 100)
            await ctx.info("Searching for networkd configuration files")
        
        # Find all .network files
        config_files = []
        for path_pattern in config_paths:
            config_files.extend(glob.glob(path_pattern))
        
        # Find all drop-in files
        dropin_files = []
        for path_pattern in dropin_paths:
            dropin_files.extend(glob.glob(path_pattern))
        
        if not config_files and not dropin_files:
            if ctx:
                await ctx.info("No networkd configuration files found")
            return {
                "success": True,
                "config_files": [],
                "interpretation": "No systemd-networkd configuration files found. The system may not be using systemd-networkd for network configuration."
            }
        
        if ctx:
            await ctx.report_progress(20, 100)
            await ctx.info(f"Found {len(config_files)} networkd configuration files and {len(dropin_files)} drop-in files")
        
        # Group drop-in files by their parent config
        dropin_map = {}
        for dropin_file in dropin_files:
            # Extract the parent config name from the drop-in path
            # e.g., /etc/systemd/network/80-wired.network.d/10-override.conf -> 80-wired.network
            dropin_dir = os.path.dirname(dropin_file)
            parent_name = os.path.basename(dropin_dir)[:-2]  # Remove the '.d' suffix
            
            if parent_name not in dropin_map:
                dropin_map[parent_name] = []
            dropin_map[parent_name].append(dropin_file)
        
        # Parse each config file
        parsed_configs = []
        for config_file in config_files:
            if ctx:
                await ctx.info(f"Parsing {os.path.basename(config_file)}")
            
            # Use configparser to parse the INI-style files
            parser = configparser.ConfigParser()
            try:
                parser.read(config_file)
                
                # Check if there are drop-in files for this config
                config_name = os.path.basename(config_file)
                if config_name in dropin_map:
                    if ctx:
                        await ctx.info(f"Merging {len(dropin_map[config_name])} drop-in files for {config_name}")
                    
                    # Parse and merge each drop-in file
                    for dropin_file in sorted(dropin_map[config_name]):
                        dropin_parser = configparser.ConfigParser()
                        dropin_parser.read(dropin_file)
                        
                        # Merge sections from drop-in file into main config
                        for section in dropin_parser.sections():
                            if section not in parser:
                                parser.add_section(section)
                            
                            # Merge options within the section
                            for option, value in dropin_parser[section].items():
                                parser[section][option] = value
                
                # Extract interface name from Match section if present
                config_interface = None
                if "Match" in parser and "Name" in parser["Match"]:
                    config_interface = parser["Match"]["Name"]
                
                # Skip if we're filtering by interface and this doesn't match
                if interface and config_interface and interface != config_interface:
                    continue
                
                # Convert to dictionary
                sections = {}
                for section in parser.sections():
                    sections[section] = dict(parser[section])
                
                # Add information about drop-ins
                dropin_info = []
                if config_name in dropin_map:
                    for dropin_file in dropin_map[config_name]:
                        dropin_info.append({
                            "path": dropin_file,
                            "name": os.path.basename(dropin_file)
                        })
                
                parsed_configs.append({
                    "path": config_file,
                    "interface": config_interface,
                    "sections": sections,
                    "dropins": dropin_info
                })
            except Exception as e:
                logger.warning(f"Error parsing {config_file}: {e}")
        
        # Handle orphaned drop-in files (those without a parent config file)
        orphaned_dropins = {}
        for parent_name, files in dropin_map.items():
            if not any(os.path.basename(config) == parent_name for config in config_files):
                orphaned_dropins[parent_name] = files
        
        if orphaned_dropins and ctx:
            await ctx.info(f"Found {len(orphaned_dropins)} orphaned drop-in directories")
        
        # Parse orphaned drop-in files
        for parent_name, files in orphaned_dropins.items():
            if ctx:
                await ctx.info(f"Parsing orphaned drop-ins for {parent_name}")
            
            # Merge all drop-ins for this parent
            merged_parser = configparser.ConfigParser()
            for dropin_file in sorted(files):
                try:
                    dropin_parser = configparser.ConfigParser()
                    dropin_parser.read(dropin_file)
                    
                    # Merge sections
                    for section in dropin_parser.sections():
                        if section not in merged_parser:
                            merged_parser.add_section(section)
                        
                        # Merge options
                        for option, value in dropin_parser[section].items():
                            merged_parser[section][option] = value
                except Exception as e:
                    logger.warning(f"Error parsing drop-in {dropin_file}: {e}")
            
            # Extract interface name if present
            config_interface = None
            if "Match" in merged_parser and "Name" in merged_parser["Match"]:
                config_interface = merged_parser["Match"]["Name"]
            
            # Skip if we're filtering by interface and this doesn't match
            if interface and config_interface and interface != config_interface:
                continue
            
            # Convert to dictionary
            sections = {}
            for section in merged_parser.sections():
                sections[section] = dict(merged_parser[section])
            
            # Add to parsed configs
            if sections:
                dropin_info = [{"path": f, "name": os.path.basename(f)} for f in files]
                parsed_configs.append({
                    "path": f"(orphaned drop-ins for {parent_name})",
                    "interface": config_interface,
                    "sections": sections,
                    "dropins": dropin_info,
                    "is_orphaned": True
                })
        
        if ctx:
            await ctx.report_progress(70, 100)
            await ctx.info(f"Successfully parsed {len(parsed_configs)} configurations")
        
        # Filter by interface if specified
        if interface:
            # Include configs that either match the interface or have no specific interface
            parsed_configs = [
                config for config in parsed_configs
                if not config["interface"] or config["interface"] == interface
            ]
        
        # Generate interpretation
        interpretation = ""
        if not parsed_configs:
            if interface:
                interpretation = f"No systemd-networkd configuration found for interface {interface}"
            else:
                interpretation = "No valid systemd-networkd configurations found"
        else:
            # Analyze configurations
            dhcp_interfaces = []
            static_interfaces = []
            
            for config in parsed_configs:
                iface = config["interface"] or "unknown"
                sections = config["sections"]
                
                if "Network" in sections:
                    network = sections["Network"]
                    
                    # Check for DHCP
                    if "DHCP" in network and network["DHCP"].lower() in ["yes", "true", "ipv4", "ipv6", "both"]:
                        dhcp_interfaces.append(iface)
                    # Check for static IP
                    elif "Address" in network:
                        static_interfaces.append(iface)
            
            # Build interpretation
            if interface:
                if interface in dhcp_interfaces:
                    interpretation = f"Interface {interface} is configured to use DHCP"
                elif interface in static_interfaces:
                    interpretation = f"Interface {interface} is configured with static IP addressing"
                else:
                    interpretation = f"Interface {interface} has systemd-networkd configuration, but IP addressing method is unclear"
            else:
                parts = []
                if dhcp_interfaces:
                    parts.append(f"{len(dhcp_interfaces)} interfaces using DHCP ({', '.join(dhcp_interfaces[:3])}{'...' if len(dhcp_interfaces) > 3 else ''})")
                if static_interfaces:
                    parts.append(f"{len(static_interfaces)} interfaces using static IP ({', '.join(static_interfaces[:3])}{'...' if len(static_interfaces) > 3 else ''})")
                
                if parts:
                    interpretation = f"Found {len(parsed_configs)} systemd-networkd configurations with " + " and ".join(parts)
                else:
                    interpretation = f"Found {len(parsed_configs)} systemd-networkd configurations, but IP addressing method is unclear"
        
        result = {
            "success": True,
            "config_files": parsed_configs,
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Config analysis complete: {interpretation}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error reading networkd configuration: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": "Failed to read networkd configuration",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)