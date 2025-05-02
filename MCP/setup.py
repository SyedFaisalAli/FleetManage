#!/usr/bin/env python3
"""
Setup script for the Network Diagnostics MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="network-diagnostics-mcp",
    version="0.1.0",
    description="MCP server for network diagnostics on Nvidia Jetson Orin Nano",
    author="FleetManage",
    packages=find_packages(),
    install_requires=[
        "fastmcp",
        "psutil",
        "netifaces2",
    ],
    entry_points={
        "console_scripts": [
            "network-diagnostics-mcp=network_diagnostics_server.server:main",
        ],
    },
    python_requires=">=3.8",
)