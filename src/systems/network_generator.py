"""
Network Generator - Cyber Hero Terminal Zero
Generates realistic local networks for Mission 1
"""

import random
from typing import Dict, List, Tuple


class Device:
    """Represents a network device"""
    def __init__(self, name: str, ip: str, mac: str, device_type: str,
                 open_ports: List[int], is_trusted: bool = True):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.device_type = device_type
        self.open_ports = open_ports
        self.is_trusted = is_trusted
        self.isolated = False

    def to_dict(self) -> Dict:
        """Convert device to dictionary"""
        return {
            'name': self.name,
            'ip': self.ip,
            'mac': self.mac,
            'type': self.device_type,
            'open_ports': self.open_ports,
            'is_trusted': self.is_trusted,
            'isolated': self.isolated
        }


class NetworkGenerator:
    """
    Generates realistic local networks with vulnerabilities
    for Mission 1: Local Network Safety
    """

    # Device templates
    DEVICE_TEMPLATES = {
        'router': {
            'name': 'Router',
            'type': 'router',
            'possible_ports': [22, 23, 80, 443, 8080],
            'risky_ports': [23],  # Telnet
            'trusted': True
        },
        'player_pc': {
            'name': 'PC-Principal',
            'type': 'computer',
            'possible_ports': [22, 80, 443, 3389],
            'risky_ports': [],
            'trusted': True
        },
        'phone': {
            'name': 'Smartphone',
            'type': 'mobile',
            'possible_ports': [443, 8080],
            'risky_ports': [],
            'trusted': True
        },
        'iot_camera': {
            'name': 'Camera-IP',
            'type': 'iot',
            'possible_ports': [23, 80, 554, 8080],
            'risky_ports': [23],  # Telnet on IoT is dangerous
            'trusted': True
        },
        'unknown_device': {
            'name': 'Device-Inconnu',
            'type': 'unknown',
            'possible_ports': [23, 445, 3389],
            'risky_ports': [23, 445],  # Telnet + SMB
            'trusted': False
        }
    }

    def __init__(self, seed: int = None):
        """
        Initialize network generator

        Args:
            seed: Random seed for reproducibility (optional)
        """
        if seed:
            random.seed(seed)

        self.network_base = "192.168.1"
        self.devices = []

    def generate_mac(self) -> str:
        """Generate random MAC address"""
        return ":".join([f"{random.randint(0, 255):02X}" for _ in range(6)])

    def generate_ip(self, host_id: int) -> str:
        """Generate IP address"""
        return f"{self.network_base}.{host_id}"

    def create_device(self, template_key: str, host_id: int) -> Device:
        """
        Create a device from template

        Args:
            template_key: Key from DEVICE_TEMPLATES
            host_id: Host ID for IP address

        Returns:
            Device object
        """
        template = self.DEVICE_TEMPLATES[template_key]

        # Randomly select 2-3 ports from possible ports
        num_ports = random.randint(2, 3)
        selected_ports = random.sample(template['possible_ports'],
                                      min(num_ports, len(template['possible_ports'])))

        # Ensure at least one risky port is included if this is a vulnerable device
        if template['risky_ports'] and random.random() > 0.3:
            risky_port = random.choice(template['risky_ports'])
            if risky_port not in selected_ports:
                selected_ports.append(risky_port)

        device = Device(
            name=template['name'],
            ip=self.generate_ip(host_id),
            mac=self.generate_mac(),
            device_type=template['type'],
            open_ports=sorted(selected_ports),
            is_trusted=template['trusted']
        )

        return device

    def generate_mission1_network(self) -> Dict:
        """
        Generate a network for Mission 1

        Network always contains:
        - Router (192.168.1.1)
        - Player PC (192.168.1.10)
        - Phone (192.168.1.20)
        - IoT Camera (192.168.1.30) - May have Telnet vulnerability
        - Unknown Device (192.168.1.50) - Always untrusted

        Returns:
            Dictionary with network configuration and devices
        """
        self.devices = []

        # Always include these devices
        self.devices.append(self.create_device('router', 1))
        self.devices.append(self.create_device('player_pc', 10))
        self.devices.append(self.create_device('phone', 20))
        self.devices.append(self.create_device('iot_camera', 30))
        self.devices.append(self.create_device('unknown_device', 50))

        # Calculate vulnerabilities
        risky_ports_found = []
        untrusted_devices = []

        for device in self.devices:
            # Check for risky ports (Telnet = 23)
            if 23 in device.open_ports:
                risky_ports_found.append({
                    'device': device.name,
                    'ip': device.ip,
                    'port': 23,
                    'service': 'Telnet'
                })

            # Check for untrusted devices
            if not device.is_trusted:
                untrusted_devices.append({
                    'name': device.name,
                    'ip': device.ip,
                    'mac': device.mac
                })

        network_config = {
            'network_id': f"net_{random.randint(1000, 9999)}",
            'subnet': f"{self.network_base}.0/24",
            'gateway': f"{self.network_base}.1",
            'devices': [d.to_dict() for d in self.devices],
            'vulnerabilities': {
                'risky_ports': risky_ports_found,
                'untrusted_devices': untrusted_devices
            },
            'security_status': 'vulnerable'
        }

        return network_config

    def generate_packets(self, network_config: Dict, count: int = 10) -> List[Dict]:
        """
        Generate fake network packets for analysis

        Args:
            network_config: Network configuration from generate_mission1_network
            count: Number of packets to generate

        Returns:
            List of packet dictionaries
        """
        packets = []
        devices = network_config['devices']

        protocols = ['TCP', 'UDP', 'ICMP']

        for i in range(count):
            # Random source and destination
            src_device = random.choice(devices)
            dst_device = random.choice([d for d in devices if d != src_device])

            protocol = random.choice(protocols)

            # For TCP/UDP, use actual open ports
            if protocol in ['TCP', 'UDP']:
                src_port = random.choice(src_device['open_ports']) if src_device['open_ports'] else random.randint(1024, 65535)
                dst_port = random.choice(dst_device['open_ports']) if dst_device['open_ports'] else random.randint(1, 1024)
            else:
                src_port = 0
                dst_port = 0

            # Generate suspicious payload for untrusted devices
            is_suspicious = not src_device['is_trusted'] or not dst_device['is_trusted']

            if is_suspicious and dst_port == 23:
                payload = "LOGIN ATTEMPT: admin:admin"
            elif is_suspicious:
                payload = "SCAN ATTEMPT"
            else:
                payload = "NORMAL TRAFFIC"

            packet = {
                'id': f"PKT_{i:04d}",
                'timestamp': f"2024-01-15 10:{i:02d}:00",
                'src_ip': src_device['ip'],
                'src_port': src_port,
                'dst_ip': dst_device['ip'],
                'dst_port': dst_port,
                'protocol': protocol,
                'length': random.randint(60, 1500),
                'payload': payload,
                'is_suspicious': is_suspicious
            }

            packets.append(packet)

        return packets


# Singleton instance
_network_generator = NetworkGenerator()


def get_network_generator() -> NetworkGenerator:
    """Get global network generator instance"""
    return _network_generator
