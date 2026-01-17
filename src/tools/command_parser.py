"""
Command Parser for CyberHero
Parses and routes player commands to appropriate tool simulators
"""

from typing import Dict, Tuple, List, Optional


class CommandParser:
    """Parses terminal commands and routes them to appropriate tools"""

    def __init__(self):
        self.command_history = []
        self.available_commands = {
            'nmap': 'Network scanning tool',
            'vpn': 'VPN anonymity tool (connect/disconnect)',
            'tor': 'TOR routing tool (start/stop)',
            'download': 'Download files from target system',
            'ls': 'List downloaded files',
            'analyze': 'Packet analysis tool',
            'crack': 'Password cracking tool',
            'help': 'Show help information',
            'objectives': 'Show mission objectives',
            'hint': 'Get a hint for the current mission',
            'clear': 'Clear the terminal screen',
            'exit': 'Exit current mission'
        }

    def parse(self, command_str: str) -> Tuple[str, List[str], Dict]:
        """
        Parse a command string into command, arguments, and options

        Args:
            command_str: Raw command string from user

        Returns:
            Tuple of (command, args, options)
        """
        if not command_str or not command_str.strip():
            return ("", [], {})

        # Add to history
        self.command_history.append(command_str)

        # Split command
        parts = command_str.strip().split()
        command = parts[0].lower() if parts else ""
        args = []
        options = {}

        # Parse arguments and options
        i = 1
        while i < len(parts):
            part = parts[i]

            # Options start with - or --
            if part.startswith('--'):
                # Long option
                opt_name = part[2:]
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    options[opt_name] = parts[i + 1]
                    i += 2
                else:
                    options[opt_name] = True
                    i += 1
            elif part.startswith('-') and len(part) > 1:
                # Short option
                opt_name = part[1:]
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    options[opt_name] = parts[i + 1]
                    i += 2
                else:
                    options[opt_name] = True
                    i += 1
            else:
                # Regular argument
                args.append(part)
                i += 1

        return (command, args, options)

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Validate if a command exists

        Args:
            command: Command name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not command:
            return (False, "No command entered")

        if command not in self.available_commands:
            # Find similar commands for suggestions
            suggestions = self.get_similar_commands(command)
            if suggestions:
                return (False, f"Unknown command '{command}'. Did you mean: {', '.join(suggestions)}?")
            else:
                return (False, f"Unknown command '{command}'. Type 'help' for available commands.")

        return (True, "")

    def get_similar_commands(self, command: str, max_distance: int = 2) -> List[str]:
        """
        Find similar command names using simple string matching

        Args:
            command: Command to find similarities for
            max_distance: Maximum character difference

        Returns:
            List of similar command names
        """
        similar = []
        for cmd in self.available_commands.keys():
            if cmd.startswith(command[:2]):  # Simple prefix matching
                similar.append(cmd)
            elif abs(len(cmd) - len(command)) <= max_distance:
                similar.append(cmd)

        return similar[:3]  # Return top 3

    def get_help(self, command: Optional[str] = None) -> str:
        """
        Get help text for commands

        Args:
            command: Specific command to get help for, or None for general help

        Returns:
            Help text string
        """
        if command:
            if command in self.available_commands:
                return self.get_detailed_help(command)
            else:
                return f"No help available for '{command}'. Type 'help' for available commands."
        else:
            # General help
            help_text = "Available Commands:\n\n"
            for cmd, desc in sorted(self.available_commands.items()):
                help_text += f"  {cmd:<12} - {desc}\n"
            help_text += "\nType 'help <command>' for detailed information about a specific command."
            return help_text

    def get_detailed_help(self, command: str) -> str:
        """Get detailed help for a specific command"""
        help_texts = {
            'nmap': """nmap - Network Mapping Tool

Usage: nmap <target> [options]

Description:
  Scans a target network to discover open ports and services.

Arguments:
  <target>    IP address or hostname to scan (e.g., 192.168.1.100)

Options:
  -p <ports>  Specify ports to scan (e.g., -p 80,443)
  -A          Enable OS detection and version scanning

Examples:
  nmap 192.168.1.100          # Basic scan
  nmap 192.168.1.100 -p 80    # Scan specific port
  nmap 192.168.1.1 -A         # Advanced scan""",

            'vpn': """vpn - Virtual Private Network Tool

Usage: vpn <action>

Description:
  Manages VPN connection for anonymous operations.

Actions:
  connect       Connect to VPN
  disconnect    Disconnect from VPN
  status        Show current VPN status

Examples:
  vpn connect     # Connect to VPN
  vpn status      # Check connection status""",

            'tor': """tor - The Onion Router

Usage: tor <action>

Description:
  Manages TOR routing for maximum anonymity.

Actions:
  start    Start TOR routing
  stop     Stop TOR routing
  status   Show TOR status

Examples:
  tor start    # Start TOR
  tor status   # Check TOR status""",

            'download': """download - File Download Tool

Usage: download <target> <file>

Description:
  Downloads files from a target system (requires prior scanning).

Arguments:
  <target>    Target IP address
  <file>      File to download

Examples:
  download 192.168.1.100 traffic.pcap    # Download packet capture""",

            'ls': """ls - List Files

Usage: ls

Description:
  Lists all files you have downloaded during the mission.

Examples:
  ls    # Show downloaded files""",

            'analyze': """analyze - Packet Analysis Tool

Usage: analyze <file>

Description:
  Analyzes network packet capture files to extract information.

Arguments:
  <file>    Path to packet capture file

Examples:
  analyze traffic.pcap     # Analyze packet capture""",

            'crack': """crack - Password Cracking Tool

Usage: crack <file> [options]

Description:
  Attempts to crack password hashes using various methods.

Arguments:
  <file>       File containing password hashes

Options:
  -w <file>    Wordlist file to use
  -t <type>    Hash type (md5, sha1, sha256)

Examples:
  crack hashes.txt -w wordlist.txt    # Crack with wordlist""",

            'objectives': """objectives - Mission Objectives

Usage: objectives

Description:
  Displays current mission objectives and progress.""",

            'hint': """hint - Mission Hint

Usage: hint

Description:
  Provides a hint for the current mission objective.""",

            'clear': """clear - Clear Screen

Usage: clear

Description:
  Clears the terminal output.""",

            'exit': """exit - Exit Mission

Usage: exit

Description:
  Exits the current mission and returns to mission hub."""
        }

        return help_texts.get(command, f"No detailed help available for '{command}'.")

    def get_command_history(self, count: int = 10) -> List[str]:
        """
        Get recent command history

        Args:
            count: Number of recent commands to return

        Returns:
            List of recent commands
        """
        return self.command_history[-count:]
