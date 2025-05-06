#!/usr/bin/env python3
"""
Network Diagnostics MCP Server - Ping Tool

This module implements the ping diagnostic tool for NetAssist.
"""

import logging
import subprocess
import re
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger("netmcp")

async def run_ping_impl(host: str, count: int = 4, ctx = None) -> Dict[str, Any]:
    """
    Ping a host and interpret the results.
    
    Args:
        host: The hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
        ctx: The MCP context
        
    Returns:
        Dict containing the ping results and interpretation
    """
    
    logger.info(f"Running ping to {host} with count {count}")
    
    if ctx:
        await ctx.report_progress(0, 100)
        await ctx.info(f"Pinging {host} with {count} packets")
    
    try:
        # Construct the ping command based on count
        cmd = ["ping", "-c", str(count), host]
        
        # Execute the ping command
        if ctx:
            await ctx.report_progress(10, 100)
            await ctx.info(f"Executing command: {' '.join(cmd)}")
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if ctx:
            await ctx.report_progress(50, 100)
            await ctx.info("Processing ping results")
        
        # Check if the command was successful
        if process.returncode != 0:
            error_msg = process.stderr.strip() or "Unknown error occurred"
            return {
                "success": False,
                "message": f"Ping to {host} failed: {error_msg}",
                "error": error_msg
            }
        
        # Parse the output to extract statistics
        output = process.stdout
        
        # Extract packet statistics using regex
        packets_stats = re.search(r'(\d+) packets transmitted, (\d+) (?:packets)?\s?received, (\d+)% packet loss', output)
        if packets_stats:
            sent = int(packets_stats.group(1))
            received = int(packets_stats.group(2))
            loss_percentage = int(packets_stats.group(3))
        else:
            # Fallback if regex doesn't match
            sent = count
            received = 0
            loss_percentage = 100
        
        # Extract timing information
        timing_stats = re.search(r'min\/avg\/max(?:\/mdev)? = ([\d.]+)\/([\d.]+)\/([\d.]+)(?:\/([\d.]+))?', output)
        if timing_stats:
            min_rtt = f"{timing_stats.group(1)} ms"
            avg_rtt = f"{timing_stats.group(2)} ms"
            max_rtt = f"{timing_stats.group(3)} ms"
        else:
            # Fallback if regex doesn't match
            min_rtt = "N/A"
            avg_rtt = "N/A"
            max_rtt = "N/A"
        
        # Provide interpretation based on the results
        if received == 0:
            interpretation = f"No response from {host}. Host may be down or unreachable."
        elif loss_percentage > 50:
            interpretation = f"Poor network connectivity to {host} with {loss_percentage}% packet loss. Network is highly unstable."
        elif loss_percentage > 20:
            interpretation = f"Degraded network connectivity to {host} with {loss_percentage}% packet loss. Network may be congested."
        elif loss_percentage > 0:
            interpretation = f"Generally good network connectivity to {host} with minor packet loss ({loss_percentage}%)."
        else:
            # Parse the average RTT to provide more detailed interpretation
            try:
                avg_rtt_value = float(timing_stats.group(2)) if timing_stats else 0
                
                if avg_rtt_value < 10:
                    rtt_quality = "excellent (low latency)"
                elif avg_rtt_value < 50:
                    rtt_quality = "good"
                elif avg_rtt_value < 100:
                    rtt_quality = "acceptable"
                elif avg_rtt_value < 200:
                    rtt_quality = "somewhat high"
                else:
                    rtt_quality = "high (potential latency issues)"
                
                interpretation = f"Network connectivity to {host} is good with no packet loss. Round-trip time is {rtt_quality}."
            except (ValueError, TypeError):
                interpretation = f"Network connectivity to {host} is good with no packet loss."
        
        result = {
            "success": True,
            "message": f"Ping to {host} completed successfully",
            "results": {
                "sent": sent,
                "received": received,
                "loss_percentage": loss_percentage,
                "min_rtt": min_rtt,
                "avg_rtt": avg_rtt,
                "max_rtt": max_rtt,
                "raw_output": output
            },
            "interpretation": interpretation
        }
        
        if ctx:
            await ctx.report_progress(90, 100)
            await ctx.info(f"Ping complete: {interpretation}")
        
        return result
        
    except subprocess.TimeoutExpired:
        error_msg = f"Ping to {host} timed out after 30 seconds"
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "error": "Command timed out"
        }
    except Exception as e:
        error_msg = f"Error executing ping: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.info(error_msg)
        return {
            "success": False,
            "message": f"Failed to ping {host}",
            "error": str(e)
        }
    finally:
        if ctx:
            await ctx.report_progress(100, 100)