import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import subprocess

# Assuming the file is in the path relative to the project root
# Adjust the import path if your project structure is different
try:
    from netmcp.nettools.ping import run_ping_impl
except ImportError:
    # Fallback for running tests directly if path issues arise
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from netmcp.nettools.ping import run_ping_impl


class TestPingImpl(unittest.TestCase):

    def test_successful_ping_no_loss(self):
        """Test successful ping with no packet loss."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = 0
        mock_process.stdout = """
PING google.com (142.250.191.142) 56(84) bytes of data.
64 bytes from ord38s34-in-f14.1e100.net (142.250.191.142): icmp_seq=1 ttl=116 time=8.500 ms
64 bytes from ord38s34-in-f14.1e100.net (142.250.191.142): icmp_seq=2 ttl=116 time=8.650 ms
64 bytes from ord38s34-in-f14.1e100.net (142.250.191.142): icmp_seq=3 ttl=116 time=8.700 ms
64 bytes from ord38s34-in-f14.1e100.net (142.250.191.142): icmp_seq=4 ttl=116 time=8.800 ms

--- google.com ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 8.500/8.650/8.800/0.100 ms
"""
        mock_process.stderr = ""

        with patch('subprocess.run', return_value=mock_process) as mock_run:
            # Use asyncio.run() to execute the async function in a sync test method
            result = asyncio.run(run_ping_impl("google.com", count=4))

            mock_run.assert_called_once_with(
                ["ping", "-c", "4", "google.com"],
                capture_output=True, text=True, timeout=30
            )
            self.assertTrue(result["success"])
            self.assertEqual(result["results"]["sent"], 4)
            self.assertEqual(result["results"]["received"], 4)
            self.assertEqual(result["results"]["loss_percentage"], 0)
            self.assertEqual(result["results"]["min_rtt"], "8.500 ms")
            self.assertEqual(result["results"]["avg_rtt"], "8.650 ms")
            self.assertEqual(result["results"]["max_rtt"], "8.800 ms")
            self.assertIn("good with no packet loss", result["interpretation"])
            self.assertIn("excellent (low latency)", result["interpretation"])

    def test_ping_with_packet_loss(self):
        """Test ping with some packet loss."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = 0
        mock_process.stdout = """
PING example.com (93.184.216.34) 56(84) bytes of data.
64 bytes from 93.184.216.34: icmp_seq=1 ttl=56 time=12.000 ms
64 bytes from 93.184.216.34: icmp_seq=3 ttl=56 time=13.000 ms

--- example.com ping statistics ---
4 packets transmitted, 2 packets received, 50% packet loss, time 3000ms
rtt min/avg/max/mdev = 12.000/12.500/13.000/0.500 ms
"""
        mock_process.stderr = ""

        with patch('subprocess.run', return_value=mock_process) as mock_run:
            result = asyncio.run(run_ping_impl("example.com", count=4))

            mock_run.assert_called_once_with(
                ["ping", "-c", "4", "example.com"],
                capture_output=True, text=True, timeout=30
            )
            self.assertTrue(result["success"])
            self.assertEqual(result["results"]["sent"], 4)
            self.assertEqual(result["results"]["received"], 2)
            self.assertEqual(result["results"]["loss_percentage"], 50)
            self.assertEqual(result["results"]["min_rtt"], "12.000 ms")
            self.assertEqual(result["results"]["avg_rtt"], "12.500 ms")
            self.assertEqual(result["results"]["max_rtt"], "13.000 ms")
            # Interpretation changes based on loss percentage
            self.assertIn("Degraded network connectivity", result["interpretation"])
            self.assertIn("50% packet loss", result["interpretation"])

    def test_ping_failure_return_code(self):
        """Test ping failure due to non-zero return code."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = 2
        mock_process.stdout = ""
        mock_process.stderr = "ping: unknown host unknown.host"

        with patch('subprocess.run', return_value=mock_process) as mock_run:
            result = asyncio.run(run_ping_impl("unknown.host", count=1))

            mock_run.assert_called_once_with(
                ["ping", "-c", "1", "unknown.host"],
                capture_output=True, text=True, timeout=30
            )
            self.assertFalse(result["success"])
            self.assertIn("Ping to unknown.host failed", result["message"])
            self.assertEqual(result["error"], "ping: unknown host unknown.host")

    def test_ping_timeout(self):
        """Test ping failure due to timeout."""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd=["ping", "-c", "1", "timeout.host"], timeout=30)) as mock_run:
            result = asyncio.run(run_ping_impl("timeout.host", count=1))

            mock_run.assert_called_once_with(
                ["ping", "-c", "1", "timeout.host"],
                capture_output=True, text=True, timeout=30
            )
            self.assertFalse(result["success"])
            self.assertIn("Ping to timeout.host timed out", result["message"])
            self.assertEqual(result["error"], "Command timed out")

    def test_ping_regex_parse_failure_packets(self):
        """Test handling when packet stats regex fails."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = 0
        # Malformed output missing packet stats line
        mock_process.stdout = """
PING malformed.com (1.2.3.4) 56(84) bytes of data.
64 bytes from 1.2.3.4: icmp_seq=1 ttl=56 time=10.000 ms
--- malformed.com ping statistics ---
rtt min/avg/max/mdev = 10.000/10.000/10.000/0.000 ms
"""
        mock_process.stderr = ""

        with patch('subprocess.run', return_value=mock_process) as mock_run:
            result = asyncio.run(run_ping_impl("malformed.com", count=1))

            mock_run.assert_called_once_with(
                ["ping", "-c", "1", "malformed.com"],
                capture_output=True, text=True, timeout=30
            )
            self.assertTrue(result["success"])
            # Check fallback values when packet regex fails
            self.assertEqual(result["results"]["sent"], 1) # Falls back to count
            self.assertEqual(result["results"]["received"], 0)
            self.assertEqual(result["results"]["loss_percentage"], 100)
            # Timing might still parse correctly
            self.assertEqual(result["results"]["min_rtt"], "10.000 ms")
            self.assertEqual(result["results"]["avg_rtt"], "10.000 ms")
            self.assertEqual(result["results"]["max_rtt"], "10.000 ms")
            # Interpretation reflects 100% loss
            self.assertIn("No response from malformed.com", result["interpretation"])

    def test_ping_with_context(self):
        """Test ping with a mock context (basic check that it doesn't break)."""
        mock_process = MagicMock(spec=subprocess.CompletedProcess)
        mock_process.returncode = 0
        mock_process.stdout = """
PING ctx.com (1.1.1.1) 56(84) bytes of data.
--- ctx.com ping statistics ---
1 packets transmitted, 1 packets received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 1.000/1.000/1.000/0.000 ms
"""
        mock_process.stderr = ""

        # Use AsyncMock for the context object as its methods are awaited
        mock_ctx = AsyncMock()
        # AsyncMock automatically makes attributes like report_progress and info awaitable AsyncMocks

        with patch('subprocess.run', return_value=mock_process) as mock_run:
            # Pass the async mock context
            result = asyncio.run(run_ping_impl("ctx.com", count=1, ctx=mock_ctx))

            mock_run.assert_called_once()
            self.assertTrue(result["success"])
            # Add assertions for context calls if they were implemented and needed testing
            # e.g., mock_ctx.info.assert_any_call("Pinging ctx.com with 1 packets")


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    unittest.main()