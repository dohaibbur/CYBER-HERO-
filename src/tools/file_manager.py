"""
File Manager for CyberHero
Simulates downloading files from target systems
"""

from typing import Tuple, Dict, List


class FileManager:
    """Simulates file downloads and management during missions"""

    def __init__(self, settings=None):
        self.settings = settings
        self.downloaded_files = []

        # Available files on different target systems (discovered after scanning)
        self.target_files = {
            "192.168.1.100": {
                "traffic.pcap": {
                    "size": "2.4 MB",
                    "description": "Network packet capture file",
                    "requires_scan": True
                },
                "system.log": {
                    "size": "156 KB",
                    "description": "System log file",
                    "requires_scan": True
                }
            }
        }

    def download(self, target: str, filename: str, scanned_targets: List[str]) -> Tuple[str, Dict]:
        """
        Download a file from target system

        Args:
            target: Target IP address
            filename: File to download
            scanned_targets: List of targets that have been scanned

        Returns:
            Tuple of (output_text, metadata)
        """
        # Check if target exists
        if target not in self.target_files:
            return (f"""Error: Target '{target}' not recognized.

You must scan a target with nmap before downloading files from it.

Usage: download <target> <filename>
Example: download 192.168.1.100 traffic.pcap
""", {"success": False})

        # Check if target has been scanned
        if target not in scanned_targets:
            return (f"""Error: Target '{target}' has not been scanned yet.

You must first scan the target with nmap to discover available files.

Try: nmap {target}
Then: download {target} <filename>
""", {"success": False})

        # Check if file exists on target
        if filename not in self.target_files[target]:
            available_files = list(self.target_files[target].keys())
            return (f"""Error: File '{filename}' not found on target {target}.

Available files on this target:
{chr(10).join([f"  - {f}" for f in available_files])}

Usage: download {target} <filename>
""", {"success": False})

        # Check if already downloaded
        if filename in self.downloaded_files:
            return (f"""File '{filename}' already downloaded.

Use 'ls' to see all downloaded files.
Use 'analyze {filename}' to analyze it.
""", {"success": False})

        # Download the file
        file_info = self.target_files[target][filename]

        output = f"""Initiating download from {target}...

Connecting to target...
Authenticating...
Locating file '{filename}'...
Starting transfer...

████████████████████████████████████████ 100%

Download complete!

File: {filename}
Size: {file_info['size']}
Type: {file_info['description']}

File saved to local directory.
Use 'ls' to view all files.
Use 'analyze {filename}' to examine the contents.
"""

        # Add to downloaded files
        self.downloaded_files.append(filename)

        # Educational note
        if self.settings is None or self.settings.is_educational_mode():
            output += f"""\n[EDUCATIONAL NOTE]
File exfiltration is the process of copying files from a target system. In real
penetration testing, this requires:

1. ACCESS: You need valid credentials or exploit to access the system
2. DISCOVERY: Use commands like 'ls', 'dir', or 'find' to locate files
3. TRANSFER: Use tools like SCP, FTP, or HTTP to download files
4. STEALTH: Avoid detection by using encryption and timing transfers carefully

In this mission, the coffee shop owner authorized you to download network
captures for investigation. Always ensure you have proper authorization before
accessing systems!
"""

        metadata = {
            "success": True,
            "filename": filename,
            "target": target,
            "downloaded_files": self.downloaded_files.copy()
        }

        return (output, metadata)

    def list_files(self) -> Tuple[str, Dict]:
        """
        List all downloaded files

        Returns:
            Tuple of (output_text, metadata)
        """
        if not self.downloaded_files:
            return ("""No files downloaded yet.

Use 'download <target> <filename>' to download files from scanned targets.
After scanning a target with nmap, you can download available files.

Example workflow:
  1. nmap 192.168.1.100
  2. download 192.168.1.100 traffic.pcap
  3. analyze traffic.pcap
""", {"success": True, "file_count": 0})

        output = f"""Downloaded Files ({len(self.downloaded_files)}):

"""
        for i, filename in enumerate(self.downloaded_files, 1):
            # Find file info
            file_info = None
            for target_files in self.target_files.values():
                if filename in target_files:
                    file_info = target_files[filename]
                    break

            if file_info:
                output += f"{i}. {filename} ({file_info['size']}) - {file_info['description']}\n"
            else:
                output += f"{i}. {filename}\n"

        output += f"""
You can analyze these files with the 'analyze' command.
Example: analyze {self.downloaded_files[0]}
"""

        metadata = {
            "success": True,
            "file_count": len(self.downloaded_files),
            "files": self.downloaded_files.copy()
        }

        return (output, metadata)

    def has_file(self, filename: str) -> bool:
        """Check if a file has been downloaded"""
        return filename in self.downloaded_files

    def execute(self, command: str, args: list, options: dict, scanned_targets: List[str]) -> Tuple[str, Dict]:
        """
        Execute file management commands

        Args:
            command: Command name ('download' or 'ls')
            args: Command arguments
            options: Command options
            scanned_targets: List of scanned targets

        Returns:
            Tuple of (output_text, metadata)
        """
        if command == "download":
            if len(args) < 2:
                return ("""Usage: download <target> <filename>

Download a file from a target system.

Arguments:
  <target>     Target IP address (must be scanned first)
  <filename>   Name of file to download

Example:
  download 192.168.1.100 traffic.pcap

Note: You must scan a target with nmap before downloading files.
""", {"success": False})

            target = args[0]
            filename = args[1]
            return self.download(target, filename, scanned_targets)

        elif command == "ls":
            return self.list_files()

        else:
            return (f"Unknown file management command: {command}", {"success": False})
