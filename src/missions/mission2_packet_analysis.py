"""
Mission 2: Analyse de Paquets et Detection d'Intrusion
Packet Analysis and Intrusion Detection Mission

Objectives:
- Download and use Wireshark from the Marketplace
- Analyze network traffic in packet capture
- Identify suspicious packets and threats
- Report findings about the intruder
"""

from typing import Dict, List, Tuple, Optional


class Mission2PacketAnalysis:
    """
    Mission 2: Packet Analysis and Intrusion Detection

    Player must:
    1. Download Wireshark from the Marketplace
    2. Open Wireshark from Net Scanner
    3. Identify the suspicious IP address
    4. Find all threat types in the capture
    5. Complete the mission report
    """

    def __init__(self, profile_data: Dict):
        """
        Initialize Mission 2

        Args:
            profile_data: Player profile with progress
        """
        self.profile_data = profile_data

        # Mission state - objectives to complete
        self.objectives = {
            'download_wireshark': {
                'title': 'Telecharger Wireshark',
                'description': 'Allez dans le Navigateur > Market et telecharger Wireshark',
                'completed': False,
                'required': True,
                'hint': "Ouvrez le Navigateur depuis le bureau, puis allez dans l'onglet Market."
            },
            'open_wireshark': {
                'title': 'Ouvrir Wireshark',
                'description': 'Lancez Wireshark depuis Net Scanner',
                'completed': False,
                'required': True,
                'hint': "Ouvrez Net Scanner sur le bureau, puis double-cliquez sur Wireshark."
            },
            'find_suspicious_ip': {
                'title': 'Identifier l\'IP suspecte',
                'description': 'Trouvez l\'adresse IP de l\'appareil inconnu (intrus)',
                'completed': False,
                'required': True,
                'correct_answer': '192.168.1.66',
                'hint': "Utilisez le filtre 'suspicious' dans Wireshark pour voir les paquets suspects."
            },
            'identify_threats': {
                'title': 'Identifier les menaces',
                'description': 'Trouvez les 5 types de menaces dans la capture',
                'completed': False,
                'required': True,
                'found_threats': [],
                'target_threats': ['telnet_scan', 'port_scan', 'discovery', 'printer_exploit', 'exfiltration'],
                'hint': "Cliquez sur chaque paquet suspect pour voir les details et le type de menace."
            },
            'complete_report': {
                'title': 'Completer le rapport',
                'description': 'Soumettez votre rapport d\'analyse',
                'completed': False,
                'required': True,
                'hint': "Une fois toutes les menaces identifiees, le rapport sera automatiquement genere."
            }
        }

        # Tracking
        self.wireshark_opened = False
        self.packets_viewed = []
        self.suspicious_packets_found = []

        # The correct suspicious IP
        self.suspicious_ip = "192.168.1.66"

        # Threat types to find
        self.threat_types = {
            'telnet_scan': {
                'name': 'Scan Telnet',
                'description': 'Tentative de connexion sur le port 23 (Telnet)',
                'severity': 'high'
            },
            'port_scan': {
                'name': 'Scan de Ports',
                'description': 'Analyse des ports ouverts sur la machine cible',
                'severity': 'medium'
            },
            'discovery': {
                'name': 'Decouverte Reseau',
                'description': 'Broadcast pour identifier les appareils du reseau',
                'severity': 'medium'
            },
            'printer_exploit': {
                'name': 'Exploitation Imprimante',
                'description': 'Tentative d\'exploitation via le port 9100',
                'severity': 'high'
            },
            'exfiltration': {
                'name': 'Exfiltration de Donnees',
                'description': 'Transfert suspect de donnees vers une IP externe',
                'severity': 'critical'
            }
        }

    def check_wireshark_downloaded(self) -> bool:
        """Check if Wireshark has been downloaded"""
        downloaded_tools = self.profile_data.get('downloaded_tools', [])
        if 'wireshark' in downloaded_tools:
            self.objectives['download_wireshark']['completed'] = True
            return True
        return False

    def mark_wireshark_opened(self):
        """Mark that Wireshark was opened"""
        if self.check_wireshark_downloaded():
            self.wireshark_opened = True
            self.objectives['open_wireshark']['completed'] = True

    def submit_suspicious_ip(self, ip_address: str) -> bool:
        """
        Validate submitted suspicious IP

        Args:
            ip_address: The IP address submitted by player

        Returns:
            True if correct
        """
        if ip_address.strip() == self.suspicious_ip:
            self.objectives['find_suspicious_ip']['completed'] = True
            return True
        return False

    def report_threat_found(self, threat_type: str) -> bool:
        """
        Record a found threat

        Args:
            threat_type: The type of threat found

        Returns:
            True if valid threat type
        """
        if threat_type in self.threat_types:
            if threat_type not in self.objectives['identify_threats']['found_threats']:
                self.objectives['identify_threats']['found_threats'].append(threat_type)

            # Check if all threats found
            found = self.objectives['identify_threats']['found_threats']
            target = self.objectives['identify_threats']['target_threats']
            if all(t in found for t in target):
                self.objectives['identify_threats']['completed'] = True

            return True
        return False

    def check_report_complete(self) -> bool:
        """Check if mission report can be completed"""
        # Report is complete when:
        # 1. Suspicious IP is identified
        # 2. All threats are found
        if (self.objectives['find_suspicious_ip']['completed'] and
            self.objectives['identify_threats']['completed']):
            self.objectives['complete_report']['completed'] = True
            return True
        return False

    def update_progress(self) -> Dict:
        """
        Update mission progress based on current state

        Returns:
            Updated objectives dict
        """
        # Check each objective
        self.check_wireshark_downloaded()

        if self.wireshark_opened:
            self.objectives['open_wireshark']['completed'] = True

        self.check_report_complete()

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
            'title': 'Mission 2: Analyse de Paquets et Detection d\'Intrusion',
            'difficulty': 'Intermediaire',
            'estimated_time': '20-30 minutes',
            'description': """
Alerte! Une activite suspecte a ete detectee sur ton reseau.

Apres avoir securise le reseau dans la Mission 1, tu dois maintenant
analyser le trafic capture pour identifier la source de l'intrusion.

CONTEXTE:
Un appareil inconnu s'est connecte a ton reseau et a commence a
scanner les autres appareils. Tu dois utiliser Wireshark pour
analyser les paquets et comprendre ce qui s'est passe.

OUTILS NECESSAIRES:
- Navigateur > Market : Telecharger Wireshark
- Net Scanner : Lancer Wireshark
- Wireshark : Analyser les paquets

OBJECTIFS PRINCIPAUX:
1. Telecharger Wireshark depuis le Marketplace
2. Ouvrir Wireshark depuis Net Scanner
3. Identifier l'adresse IP de l'intrus
4. Trouver les 5 types de menaces dans la capture
5. Completer le rapport de mission

RECOMPENSES:
- +50 XP
- Badge "Packet Detective"
- Debloquer Mission 3

Bonne chance, analyste!
            """.strip(),
            'objectives': self.objectives
        }

    def award_completion_rewards(self) -> Dict:
        """Award XP and badges for completing the mission"""
        rewards = {
            'xp': 300,
            'badges': ['Packet Detective'],
            'unlocked_missions': ['mission3'],
            'title': 'Mission 2 Terminee!',
            'message': """
Excellent travail, analyste!

Tu as reussi a analyser le trafic reseau et identifier l'intrus.
Voici ce que tu as decouvert:

INTRUS: 192.168.1.66 (appareil inconnu)

MENACES DETECTEES:
- Scan Telnet (port 23)
- Scan de ports multiples
- Decouverte reseau (broadcast)
- Tentative d'exploitation imprimante
- Exfiltration de donnees

Tes competences en analyse de paquets se sont nettement ameliorees.
Tu es pret pour des defis plus complexes!

RECOMPENSES OBTENUES:
- +300 XP
- Reputation: Respectable
- Badge "Packet Detective"
- Mission 3 debloquee

Continue comme ca!
            """.strip()
        }

        # Update profile
        progress = self.profile_data.get('progress', {})
        progress['xp'] = progress.get('xp', 0) + rewards['xp']
        progress['level'] = 'Respectable'
        progress['badges'] = progress.get('badges', [])

        if 'Packet Detective' not in progress['badges']:
            progress['badges'].append('Packet Detective')

        progress['missions_completed'] = progress.get('missions_completed', [])
        if 'mission2' not in progress['missions_completed']:
            progress['missions_completed'].append('mission2')

        progress['unlocked_missions'] = progress.get('unlocked_missions', [])
        if 'mission3' not in progress['unlocked_missions']:
            progress['unlocked_missions'].append('mission3')

        return rewards

    def get_hint(self, objective_id: str) -> str:
        """Get hint for specific objective"""
        if objective_id in self.objectives:
            return self.objectives[objective_id].get('hint', "Continue d'explorer les outils disponibles.")
        return "Continue d'explorer les outils disponibles."

    def get_threat_info(self, threat_type: str) -> Optional[Dict]:
        """Get information about a specific threat type"""
        return self.threat_types.get(threat_type)

    def get_found_threats(self) -> List[str]:
        """Get list of threats found so far"""
        return self.objectives['identify_threats']['found_threats']

    def get_remaining_threats(self) -> List[str]:
        """Get list of threats not yet found"""
        found = self.objectives['identify_threats']['found_threats']
        target = self.objectives['identify_threats']['target_threats']
        return [t for t in target if t not in found]

    def generate_report(self) -> str:
        """Generate the mission report text"""
        found_threats = self.get_found_threats()
        remaining = self.get_remaining_threats()

        report = """
=== RAPPORT D'ANALYSE DE PAQUETS ===

INTRUS IDENTIFIE: {}
STATUT: {}

MENACES DETECTEES ({}/5):
""".format(
            self.suspicious_ip if self.objectives['find_suspicious_ip']['completed'] else "Non identifie",
            "CONFIRME" if self.objectives['find_suspicious_ip']['completed'] else "EN ATTENTE",
            len(found_threats)
        )

        for threat_id in found_threats:
            threat = self.threat_types.get(threat_id, {})
            report += f"  [X] {threat.get('name', threat_id)}: {threat.get('description', '')}\n"

        for threat_id in remaining:
            report += f"  [ ] ???: Menace non identifiee\n"

        report += """
RECOMMANDATIONS:
- Isoler l'appareil suspect (192.168.1.66)
- Bloquer le port Telnet (23) sur le routeur
- Verifier l'integrite de l'imprimante
- Surveiller le trafic sortant vers 185.234.72.100

=== FIN DU RAPPORT ===
"""
        return report
