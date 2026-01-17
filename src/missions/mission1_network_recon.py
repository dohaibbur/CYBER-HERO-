"""
Mission 1: Reconnaissance et Cartographie Réseau
Network Reconnaissance and Mapping Mission

Objectives:
- Use terminal and basic commands
- Discover active hosts on network (ping, nmap)
- Identify services and open ports
- Understand network architecture
"""

import pygame
from typing import Dict, Tuple, Optional
from src.systems.network_generator import get_network_generator


class Mission1NetworkRecon:
    """
    Mission 1: Network Reconnaissance and Mapping

    Player must:
    1. Scan the local network
    2. Identify all devices
    3. Find open ports (especially risky ones)
    4. Analyze network packets
    5. Secure the network
    """

    def __init__(self, profile_data: Dict):
        """
        Initialize Mission 1

        Args:
            profile_data: Player profile with progress
        """
        self.profile_data = profile_data

        # Generate unique network for this mission
        generator = get_network_generator()
        self.network_config = generator.generate_mission1_network()
        self.packets = generator.generate_packets(self.network_config, count=15)

        # Mission state
        self.objectives = {
            'scan_network': {
                'title': 'Scanner le réseau local',
                'description': 'Utiliser la commande "scan network" dans le Terminal',
                'completed': False,
                'required': True
            },
            'identify_devices': {
                'title': 'Identifier tous les périphériques',
                'description': 'Découvrir les 5 appareils sur le réseau',
                'completed': False,
                'required': True,
                'progress': 0,
                'target': 5
            },
            'find_risky_ports': {
                'title': 'Trouver les ports dangereux',
                'description': 'Identifier le port 23 (Telnet) ouvert',
                'completed': False,
                'required': True,
                'found_ports': []
            },
            'analyze_packets': {
                'title': 'Analyser les paquets réseau',
                'description': 'Répondre correctement aux questions sur les paquets',
                'completed': False,
                'required': True,
                'questions_answered': 0,
                'questions_total': 5
            },
            'isolate_threats': {
                'title': 'Isoler les périphériques non fiables',
                'description': 'Isoler tous les appareils suspects',
                'completed': False,
                'required': True,
                'isolated_count': 0,
                'target_count': len(self.network_config['vulnerabilities']['untrusted_devices'])
            },
            'block_risky_ports': {
                'title': 'Bloquer les ports à risque',
                'description': 'Bloquer le port 23 (Telnet)',
                'completed': False,
                'required': True,
                'blocked_ports': []
            },
            'final_audit': {
                'title': 'Audit de sécurité final',
                'description': 'Exécuter "audit system" et obtenir RESEAU SECURISE',
                'completed': False,
                'required': True
            }
        }

        # Track player actions
        self.commands_used = []
        self.devices_discovered = []
        self.packets_analyzed = []

    def check_scan_network_complete(self, terminal_state: Dict) -> bool:
        """Check if network scan objective is complete"""
        # Check if player ran 'scan network' command
        if 'scan network' in self.commands_used:
            self.objectives['scan_network']['completed'] = True
            return True
        return False

    def check_identify_devices_complete(self, terminal_state: Dict) -> bool:
        """Check if all devices have been discovered"""
        # Count discovered devices
        discovered = len(self.devices_discovered)
        self.objectives['identify_devices']['progress'] = discovered

        if discovered >= self.objectives['identify_devices']['target']:
            self.objectives['identify_devices']['completed'] = True
            return True
        return False

    def check_find_risky_ports_complete(self, terminal_state: Dict) -> bool:
        """Check if risky ports have been identified"""
        # Check for port 23 in found ports
        risky_ports = self.network_config['vulnerabilities']['risky_ports']

        for vuln in risky_ports:
            if vuln['port'] == 23:
                if 23 in self.objectives['find_risky_ports']['found_ports']:
                    self.objectives['find_risky_ports']['completed'] = True
                    return True

        return False

    def check_isolate_threats_complete(self, isolated_devices: list) -> bool:
        """Check if all untrusted devices are isolated"""
        untrusted = self.network_config['vulnerabilities']['untrusted_devices']

        isolated_count = 0
        for device in untrusted:
            if device['mac'] in isolated_devices:
                isolated_count += 1

        self.objectives['isolate_threats']['isolated_count'] = isolated_count

        if isolated_count >= self.objectives['isolate_threats']['target_count']:
            self.objectives['isolate_threats']['completed'] = True
            return True

        return False

    def check_block_risky_ports_complete(self, blocked_ports: list) -> bool:
        """Check if risky ports are blocked"""
        if 23 in blocked_ports:
            self.objectives['block_risky_ports']['completed'] = True
            self.objectives['block_risky_ports']['blocked_ports'] = blocked_ports
            return True

        return False

    def check_final_audit_complete(self, isolated_devices: list, blocked_ports: list) -> bool:
        """Check if final audit shows secure network"""
        # Network is secure if:
        # 1. All untrusted devices are isolated
        # 2. All risky ports (23) are blocked

        untrusted = self.network_config['vulnerabilities']['untrusted_devices']
        untrusted_isolated = all(device['mac'] in isolated_devices for device in untrusted)

        risky_ports = self.network_config['vulnerabilities']['risky_ports']
        risky_blocked = all(vuln['port'] in blocked_ports for vuln in risky_ports)

        if untrusted_isolated and risky_blocked:
            self.objectives['final_audit']['completed'] = True
            return True

        return False

    def update_progress(self, terminal_state: Dict) -> Dict:
        """
        Update mission progress based on terminal state

        Args:
            terminal_state: Current state from Terminal app
                {
                    'commands_history': [...],
                    'blocked_ports': [...],
                    'isolated_devices': [...],
                    'network_scanned': bool,
                    'devices_discovered': [...]
                }

        Returns:
            Updated objectives dict
        """
        # Update tracked data
        self.commands_used = terminal_state.get('commands_history', [])
        self.devices_discovered = terminal_state.get('devices_discovered', [])

        blocked_ports = terminal_state.get('blocked_ports', [])
        isolated_devices = terminal_state.get('isolated_devices', [])

        # Check each objective
        self.check_scan_network_complete(terminal_state)
        self.check_identify_devices_complete(terminal_state)
        self.check_isolate_threats_complete(isolated_devices)
        self.check_block_risky_ports_complete(blocked_ports)
        self.check_final_audit_complete(isolated_devices, blocked_ports)

        return self.objectives

    def is_mission_complete(self) -> bool:
        """Check if all required objectives are complete"""
        for obj_id, obj_data in self.objectives.items():
            if obj_data['required'] and not obj_data['completed']:
                return False
        return True

    def get_completion_percentage(self) -> float:
        """Calculate mission completion percentage"""
        total_required = sum(1 for obj in self.objectives.values() if obj['required'])
        completed = sum(1 for obj in self.objectives.values() if obj['required'] and obj['completed'])

        return (completed / total_required) * 100 if total_required > 0 else 0

    def get_mission_briefing(self) -> Dict:
        """Get full mission briefing for display"""
        return {
            'title': 'Mission 1: Reconnaissance et Cartographie Réseau',
            'difficulty': 'Débutant',
            'estimated_time': '15-20 minutes',
            'description': """
Bienvenue dans ta première mission, recrue.

Ton réseau local a été compromis. Un appareil inconnu s'est connecté et
certains services dangereux sont exposés.

Ta mission : sécuriser le réseau.

CONTEXTE:
Ton réseau domestique contient plusieurs appareils : ton PC, ton smartphone,
une caméra IoT, et ton routeur. Mais quelque chose ne va pas...

OUTILS À UTILISER:
• Terminal - Commandes réseau (scan, block, isolate)
• Net Scanner - Visualisation des appareils
• Packet Lab - Analyse du trafic réseau

OBJECTIFS PRINCIPAUX:
1. Scanner et cartographier le réseau
2. Identifier tous les périphériques
3. Trouver les ports dangereux (Telnet - port 23)
4. Analyser les paquets suspects
5. Isoler les appareils non fiables
6. Bloquer les ports à risque
7. Audit de sécurité final

RÉCOMPENSES:
• +30 XP
• Badge "Network Defender"
• Débloquer Mission 2

Bonne chance, cyber héros !
            """.strip(),
            'objectives': self.objectives,
            'network_info': {
                'subnet': self.network_config['subnet'],
                'gateway': self.network_config['gateway'],
                'devices_count': len(self.network_config['devices']),
                'vulnerabilities_count': len(self.network_config['vulnerabilities']['risky_ports']) +
                                       len(self.network_config['vulnerabilities']['untrusted_devices'])
            }
        }

    def award_completion_rewards(self) -> Dict:
        """Award XP and badges for completing the mission"""
        rewards = {
            'xp': 500,
            'badges': ['Network Defender'],
            'unlocked_missions': ['mission2'],
            'title': 'Mission 1 Terminée !',
            'message': """
Excellent travail, recrue !

Tu as réussi à sécuriser le réseau. Tous les périphériques suspects ont été
isolés et les ports dangereux ont été bloqués.

Tu as démontré une excellente compréhension de la reconnaissance réseau et
des principes de base de la cybersécurité.

RÉCOMPENSES OBTENUES:
• +500 XP
• Badge "Network Defender"
• Mission 2 débloquée

Continue comme ça !
            """.strip()
        }

        # Update profile
        progress = self.profile_data.get('progress', {})
        progress['xp'] = progress.get('xp', 0) + rewards['xp']
        progress['badges'] = progress.get('badges', [])

        if 'Network Defender' not in progress['badges']:
            progress['badges'].append('Network Defender')

        progress['missions_completed'] = progress.get('missions_completed', [])
        if 'mission1' not in progress['missions_completed']:
            progress['missions_completed'].append('mission1')

        progress['unlocked_missions'] = progress.get('unlocked_missions', [])
        if 'mission2' not in progress['unlocked_missions']:
            progress['unlocked_missions'].append('mission2')

        return rewards

    def get_hint(self, objective_id: str) -> str:
        """Get hint for specific objective"""
        hints = {
            'scan_network': "Ouvre le Terminal et tape : scan network",
            'identify_devices': "Utilise 'scan network' pour voir tous les appareils. Tu devrais en trouver 5.",
            'find_risky_ports': "Cherche le port 23 (Telnet) dans la liste des ports ouverts lors du scan.",
            'analyze_packets': "Ouvre Packet Lab pour analyser le trafic réseau et répondre aux questions.",
            'isolate_threats': "Utilise 'isolate device <MAC>' pour isoler les appareils marqués comme 'INCONNU'.",
            'block_risky_ports': "Utilise 'block port 23' dans le Terminal pour bloquer Telnet.",
            'final_audit': "Tape 'audit system' dans le Terminal pour vérifier que le réseau est sécurisé."
        }

        return hints.get(objective_id, "Continue d'explorer les outils disponibles.")

    def get_network_config(self) -> Dict:
        """Get network configuration for this mission"""
        return self.network_config

    def get_packets(self) -> list:
        """Get packet capture for this mission"""
        return self.packets
