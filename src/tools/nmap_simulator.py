"""
Nmap Simulator for CyberHero
Simulates network scanning and port discovery
"""

import random
import time
from typing import Tuple, Dict, List


class NmapSimulator:
    """Simulates Nmap network scanning tool"""

    def __init__(self, settings=None):
        self.settings = settings
        # Predefined network configurations for different targets
        self.network_configs = {
            "192.168.1.100": {
                "hostname": "cafe-wifi.local",
                "os": "Linux 3.13 - 4.6",
                "ports": [
                    {"port": 22, "service": "ssh", "version": "OpenSSH 7.4"},
                    {"port": 80, "service": "http", "version": "Apache 2.4.29"},
                    {"port": 3306, "service": "mysql", "version": "MySQL 5.7"}
                ]
            },
            "192.168.1.1": {
                "hostname": "router.local",
                "os": "Linux 2.6.X",
                "ports": [
                    {"port": 80, "service": "http", "version": "lighttpd 1.4.35"},
                    {"port": 443, "service": "https", "version": "lighttpd 1.4.35"}
                ]
            },
            "10.0.0.50": {
                "hostname": "server.internal",
                "os": "Linux 4.15 - 5.6",
                "ports": [
                    {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"},
                    {"port": 80, "service": "http", "version": "nginx 1.18.0"},
                    {"port": 443, "service": "https", "version": "nginx 1.18.0"},
                    {"port": 3389, "service": "rdp", "version": "xrdp"}
                ]
            }
        }

    def scan(self, target: str, args: list, options: dict) -> Tuple[str, Dict]:
        """
        Perform network scan on target

        Args:
            target: IP address or hostname to scan
            args: Additional arguments
            options: Scan options

        Returns:
            Tuple of (output_text, metadata)
        """
        # Check if target exists in our configs
        if target not in self.network_configs:
            # Generate a simple random scan for unknown targets
            return self._scan_unknown_target(target, options)

        config = self.network_configs[target]

        # Build output
        output = f"""Starting Nmap scan on {target}...
Nmap scan report for {config['hostname']} ({target})
Host is up (0.0042s latency).

"""

        # Check for specific port scanning
        ports_to_scan = config["ports"]
        if 'p' in options:
            # Parse port option
            requested_ports = self._parse_ports(options['p'])
            ports_to_scan = [p for p in config["ports"] if p["port"] in requested_ports]

        if not ports_to_scan:
            output += "All requested ports are closed.\n"
        else:
            output += "PORT      STATE    SERVICE    VERSION\n"
            for port_info in ports_to_scan:
                port = port_info["port"]
                service = port_info["service"]
                version = port_info.get("version", "")

                output += f"{port}/tcp   open     {service:<10} {version}\n"

        # Add OS detection if -A option is used
        if 'A' in options or 'O' in options:
            output += f"\nOS Detection:\n"
            output += f"  Running: {config['os']}\n"
            output += f"  OS CPE: cpe:/o:linux:linux_kernel\n"

        output += f"\nNmap done: 1 IP address (1 host up) scanned\n"

        # Add information about available files for download
        if target == "192.168.1.100":
            output += f"""\n[SCAN ANALYSIS]
During the scan, accessible files were detected on the target:
  - traffic.pcap (2.4 MB) - Network packet capture
  - system.log (156 KB) - System log file

These files can be downloaded using: download {target} <filename>
Example: download {target} traffic.pcap
"""

        # Educational note (only if educational mode is enabled)
        if self.settings is None or self.settings.is_educational_mode():
            output += f"""\n[EDUCATIONAL NOTE]
Nmap (Network Mapper) is a powerful tool for network discovery and security auditing.

What this scan revealed:
- {len(ports_to_scan)} open port(s) found
- Services running: {', '.join([p['service'] for p in ports_to_scan])}

Open ports represent potential entry points into a system. Each service
running on an open port could have vulnerabilities that hackers might exploit.

Common ports:
  22  - SSH (Secure Shell)
  80  - HTTP (Web Server)
  443 - HTTPS (Secure Web Server)
  3306- MySQL (Database)
  3389- RDP (Remote Desktop)

⚠ Always ensure only necessary ports are open and services are up-to-date!
"""

        metadata = {
            "success": True,
            "target": target,
            "hostname": config["hostname"],
            "os": config["os"],
            "ports_found": [p["port"] for p in ports_to_scan],
            "services": [p["service"] for p in ports_to_scan]
        }

        return (output, metadata)

    def _scan_unknown_target(self, target: str, options: dict) -> Tuple[str, Dict]:
        """Scan an unknown target with generic response"""
        # Check if IP format is valid
        if not self._is_valid_ip(target):
            return (f"Error: Invalid target '{target}'. Please provide a valid IP address.", {"success": False})

        output = f"""Starting Nmap scan on {target}...
Nmap scan report for {target}
Host is up (0.087s latency).

All 1000 scanned ports on {target} are filtered or closed.

Nmap done: 1 IP address (1 host up) scanned

[NOTE] This target is not configured for this mission. Try scanning the mission target.
"""

        return (output, {"success": False, "target": target, "ports_found": []})

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    def _parse_ports(self, port_str: str) -> List[int]:
        """Parse port specification (e.g., '80,443' or '1-100')"""
        ports = []

        for part in port_str.split(','):
            if '-' in part:
                # Range
                try:
                    start, end = part.split('-')
                    ports.extend(range(int(start), int(end) + 1))
                except:
                    pass
            else:
                # Single port
                try:
                    ports.append(int(part))
                except:
                    pass

        return ports

    def execute(self, args: list, options: dict) -> Tuple[str, Dict]:
        """
        Execute nmap command

        Args:
            args: Command arguments (target, etc.)
            options: Command options (-p, -A, etc.)

        Returns:
            Tuple of (output_text, metadata)
        """
        if not args:
            return ("""Usage: nmap <target> [options]

Options:
  -p <ports>   Scan specific ports (e.g., -p 80,443 or -p 1-1000)
  -A           Enable OS detection and version scanning

Examples:
  nmap 192.168.1.100          # Scan default ports
  nmap 192.168.1.100 -p 80    # Scan port 80
  nmap 192.168.1.100 -A       # Advanced scan
""", {"success": False})

        target = args[0]
        return self.scan(target, args[1:], options)
