"""
Network Simulation System
Generates realistic but fake network data for Mission 1 pedagogical objectives
"""

import random
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class NetworkDevice:
    """Represents a device on the simulated network"""
    hostname: str
    ip_address: str
    mac_address: str
    device_type: str  # "router", "computer", "phone", "tablet", "iot"
    manufacturer: str


class NetworkSimulator:
    """
    Generates and maintains a consistent simulated network environment
    for the player to explore during Mission 1
    """

    def __init__(self, player_nickname: str = "Player"):
        self.player_nickname = player_nickname
        self.network_data = None
        self.generate_network()

    def generate_network(self):
        """Generate a fixed, consistent network scenario for all players"""

        # FIXED router (gateway) - always the same
        router_ip = "192.168.1.1"
        router_mac = "00:17:9A:2B:3C:4D"  # Fixed D-Link MAC

        # FIXED player's computer - always the same
        player_ip = "192.168.1.120"
        player_mac = "00:15:00-2B-3A-D4"  # Fixed Intel MAC (with dashes as shown in ipconfig)

        # Generate fixed other devices on network
        devices = self._generate_fixed_devices()

        # Compile network data - ALL FIXED VALUES
        self.network_data = {
            # Player's computer info
            "player": {
                "hostname": f"{self.player_nickname}-PC",
                "ip_address": player_ip,  # 192.168.1.120
                "mac_address": player_mac,  # 00:15:00-2B-3A-D4
                "subnet_mask": "255.255.255.0",
                "default_gateway": router_ip,  # 192.168.1.1
                "dns_servers": ["8.8.8.8", "8.8.4.4"],
                "dhcp_enabled": True,
                "connection_type": "Ethernet",
                "adapter_name": "Ethernet0"
            },

            # Router info
            "router": {
                "hostname": "home",
                "ip_address": router_ip,  # 192.168.1.1
                "mac_address": router_mac,  # 00:17:9A:2B:3C:4D
                "model": "D-Link DIR-825",
                "firmware": "v2.3.24"
            },

            # Other devices
            "devices": devices,

            # Network configuration
            "network": {
                "network_address": "192.168.1.0",
                "broadcast_address": "192.168.1.255",
                "subnet_mask": "255.255.255.0",
                "cidr": "192.168.1.0/24",
                "total_devices": len(devices) + 2,  # +2 for player and router
                "dhcp_range": "192.168.1.100 - 192.168.1.200"
            }
        }

    def _generate_mac(self, manufacturer: str = None) -> str:
        """Generate a realistic MAC address"""
        # MAC address prefixes for common manufacturers
        oui_prefixes = {
            "Intel": ["00:1B:77", "00:15:00", "00:1E:67"],
            "D-Link": ["00:17:9A", "00:1B:11", "00:1C:F0"],
            "TP-Link": ["50:C7:BF", "F4:F2:6D", "A4:2B:8C"],
            "Apple": ["00:23:32", "00:25:00", "34:36:3B"],
            "Samsung": ["00:1D:25", "34:AA:99", "D0:17:C2"],
            "Xiaomi": ["34:CE:00", "50:64:2B", "78:11:DC"]
        }

        if manufacturer and manufacturer in oui_prefixes:
            prefix = random.choice(oui_prefixes[manufacturer])
        else:
            # Random OUI
            prefix = f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"

        # Generate remaining 3 octets
        suffix = f"{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"

        return f"{prefix}:{suffix}"

    def _generate_fixed_devices(self) -> List[NetworkDevice]:
        """Generate fixed, consistent devices on the network - same for all players"""
        devices = [
            NetworkDevice(
                hostname="LAPTOP-MARIE",
                ip_address="192.168.1.75",
                mac_address="A4:5E:60:C2:D1:8F",
                device_type="computer",
                manufacturer="Dell"
            ),
            NetworkDevice(
                hostname="iPhone-Papa",
                ip_address="192.168.1.155",
                mac_address="34:36:3B:A7:B2:C9",
                device_type="phone",
                manufacturer="Apple"
            ),
            NetworkDevice(
                hostname="Smart-TV",
                ip_address="192.168.1.185",
                mac_address="D0:17:C2:5F:8A:3B",
                device_type="iot",
                manufacturer="Samsung"
            ),
            NetworkDevice(
                hostname="Imprimante-HP",
                ip_address="192.168.1.220",
                mac_address="B8:27:EB:4D:2E:7C",
                device_type="iot",
                manufacturer="HP"
            )
        ]
        return devices

    def get_ipconfig_output(self) -> str:
        """Generate ipconfig /all style output (Windows)"""
        player = self.network_data["player"]
        router = self.network_data["router"]

        output = f"""
Configuration IP de Windows


Carte Ethernet {player['adapter_name']} :

   Suffixe DNS propre a la connexion. . . : home
   Description. . . . . . . . . . . . . . : Intel(R) Ethernet Connection
   Adresse physique . . . . . . . . . . . : {player['mac_address']}
   DHCP activé. . . . . . . . . . . . . . : {'Oui' if player['dhcp_enabled'] else 'Non'}
   Configuration automatique activée. . . : Oui
   Adresse IPv4. . . . . . . . . . . . . : {player['ip_address']}(préféré)
   Masque de sous-réseau . . . . . . . . : {player['subnet_mask']}
   Passerelle par défaut . . . . . . . . : {player['default_gateway']}
   Serveur DHCP . . . . . . . . . . . . . : {router['ip_address']}
   Serveurs DNS . . . . . . . . . . . . . : {player['dns_servers'][0]}
                                            {player['dns_servers'][1]}
"""
        return output.strip()

    def get_arp_output(self) -> str:
        """Generate arp -a style output"""
        player = self.network_data["player"]
        router = self.network_data["router"]
        devices = self.network_data["devices"]
        network = self.network_data["network"]

        output = f"""
Interface : {player['ip_address']} --- 0xa
  Adresse Internet      Adresse physique      Type
  {router['ip_address']:<20}  {router['mac_address']:<20}  dynamique
"""

        for device in devices:
            output += f"  {device.ip_address:<20}  {device.mac_address:<20}  dynamique\n"

        output += f"  {network['broadcast_address']:<20}  ff-ff-ff-ff-ff-ff     statique\n"

        return output.strip()

    def get_ifconfig_output(self) -> str:
        """Generate ifconfig style output (Linux/Mac)"""
        player = self.network_data["player"]

        output = f"""eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet {player['ip_address']}  netmask {player['subnet_mask']}  broadcast {self.network_data['network']['broadcast_address']}
        ether {player['mac_address']}  txqueuelen 1000  (Ethernet)
        RX packets 152847  bytes 215847639 (205.8 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 98450  bytes 9847562 (9.3 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
"""
        return output.strip()

    def get_route_output(self) -> str:
        """Generate route print style output"""
        player = self.network_data["player"]
        router = self.network_data["router"]
        network = self.network_data["network"]

        output = f"""
===========================================================================
Liste d'itinéraires actifs :
Destination réseau    Masque réseau        Adr. passerelle   Adr. interface Métrique
          0.0.0.0          0.0.0.0      {router['ip_address']:<15}  {player['ip_address']:<15}     25
        127.0.0.0        255.0.0.0         Sur place         127.0.0.1     331
        127.0.0.1  255.255.255.255         Sur place         127.0.0.1     331
   {network['network_address']}  {player['subnet_mask']}         Sur place      {player['ip_address']:<15}     281
   {player['ip_address']}  255.255.255.255         Sur place      {player['ip_address']:<15}     281
 {network['broadcast_address']}  255.255.255.255         Sur place      {player['ip_address']:<15}     281
===========================================================================
"""
        return output.strip()

    def validate_mission1_data(self, submitted_data: Dict[str, str]) -> Dict[str, bool]:
        """
        Validate player's submitted data against the simulated network

        Args:
            submitted_data: Dictionary with keys like "ip_address", "mac_address", etc.

        Returns:
            Dictionary with validation results for each field
        """
        player = self.network_data["player"]
        router = self.network_data["router"]
        network = self.network_data["network"]

        results = {}

        # Validate IP address
        if "ip_address" in submitted_data:
            results["ip_address"] = submitted_data["ip_address"].strip() == player["ip_address"]

        # Validate MAC address (accept different formats)
        if "mac_address" in submitted_data:
            submitted_mac = submitted_data["mac_address"].strip().upper().replace("-", ":")
            correct_mac = player["mac_address"].upper()
            results["mac_address"] = submitted_mac == correct_mac

        # Validate gateway
        if "gateway" in submitted_data:
            results["gateway"] = submitted_data["gateway"].strip() == router["ip_address"]

        # Validate subnet mask
        if "subnet_mask" in submitted_data:
            results["subnet_mask"] = submitted_data["subnet_mask"].strip() == player["subnet_mask"]

        # Validate device count
        if "device_count" in submitted_data:
            try:
                count = int(submitted_data["device_count"])
                results["device_count"] = count == network["total_devices"]
            except ValueError:
                results["device_count"] = False

        # Validate router name
        if "router_name" in submitted_data:
            results["router_name"] = submitted_data["router_name"].strip().upper() == router["hostname"].upper()

        return results

    def get_mission1_guide(self) -> str:
        """Get the guide text for Mission 1"""
        return """
=== GUIDE: RECONNAISSANCE RESEAU ===

Objectif: Collecter des informations sur ton réseau local

COMMANDES ESSENTIELLES:

1. ipconfig /all (Windows) ou ifconfig (Linux/Mac)
   -> Affiche la configuration de ton adaptateur réseau
   -> Cherche: Adresse IPv4, Adresse physique (MAC), Passerelle

2. arp -a
   -> Affiche la table ARP (appareils connectés)
   -> Montre toutes les IP et MAC addresses du réseau

3. route print (Windows) ou route -n (Linux/Mac)
   -> Affiche la table de routage
   -> Confirme la passerelle par défaut

INFORMATIONS A EXTRAIRE:
• Ton adresse IP privée
• Ton adresse MAC
• L'adresse IP du routeur (passerelle)
• Le masque de sous-réseau
• Le nombre d'appareils connectés

Bonne chance!
"""

    def export_to_dict(self) -> Dict:
        """Export all network data as dictionary (for saving/loading)"""
        return {
            "player": self.network_data["player"],
            "router": self.network_data["router"],
            "devices": [
                {
                    "hostname": d.hostname,
                    "ip_address": d.ip_address,
                    "mac_address": d.mac_address,
                    "device_type": d.device_type,
                    "manufacturer": d.manufacturer
                }
                for d in self.network_data["devices"]
            ],
            "network": self.network_data["network"]
        }


# Global instance (initialized when profile is created)
_network_simulator = None


def get_network_simulator(player_nickname: str = "Player") -> NetworkSimulator:
    """
    Get or create the global network simulator instance
    Network is always fixed and consistent for all players

    Args:
        player_nickname: Player's nickname (only used for hostname)

    Returns:
        NetworkSimulator instance with fixed network configuration
    """
    global _network_simulator
    if _network_simulator is None:
        _network_simulator = NetworkSimulator(player_nickname)
    return _network_simulator


def reset_network_simulator():
    """Reset the global simulator (for testing or new game)"""
    global _network_simulator
    _network_simulator = None
