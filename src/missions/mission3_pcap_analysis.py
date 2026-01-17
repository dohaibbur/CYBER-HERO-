"""
Mission 3: Analyse de Fichier PCAP
Raw Packet Capture File Analysis

Objectives:
- Receive a PCAP file from Le Professeur
- Open PCAP Analyzer from Net Scanner
- Extract data from raw hex dump
- Fill in the analysis report
"""

from typing import Dict, List, Optional


class Mission3PcapAnalysis:
    """
    Mission 3: PCAP File Analysis

    Player must:
    1. Download PCAP Analyzer from Marketplace
    2. Open PCAP Analyzer from Net Scanner
    3. Analyze raw hex dump
    4. Extract: MAC addresses, IP addresses, timestamp, protocol
    5. Submit analysis report
    """

    def __init__(self, profile_data: Dict):
        """
        Initialize Mission 3

        Args:
            profile_data: Player profile with progress
        """
        self.profile_data = profile_data

        # Mission objectives
        self.objectives = {
            'download_pcap_analyzer': {
                'title': 'Telecharger PCAP Analyzer',
                'description': 'Allez dans le Navigateur > Market et telecharger PCAP Analyzer',
                'completed': False,
                'required': True,
                'hint': "Ouvrez le Navigateur depuis le bureau, puis allez dans l'onglet Market."
            },
            'open_pcap_analyzer': {
                'title': 'Ouvrir PCAP Analyzer',
                'description': 'Lancez PCAP Analyzer depuis Packet Lab',
                'completed': False,
                'required': True,
                'hint': "Ouvrez Packet Lab sur le bureau, puis double-cliquez sur PCAP Analyzer."
            },
            'extract_mac_dest': {
                'title': 'Extraire MAC Destination',
                'description': 'Trouvez l\'adresse MAC de destination',
                'completed': False,
                'required': True,
                'correct_answer': '00:1e:ec:26:d2:ac',
                'hint': "Les premiers octets des donnees Ethernet contiennent la MAC destination."
            },
            'extract_mac_src': {
                'title': 'Extraire MAC Source',
                'description': 'Trouvez l\'adresse MAC source',
                'completed': False,
                'required': True,
                'correct_answer': '26:02:06:49:6b:31',
                'hint': "Apres la MAC destination, 6 octets pour la MAC source."
            },
            'extract_ip_src': {
                'title': 'Extraire IP Source',
                'description': 'Trouvez l\'adresse IP source',
                'completed': False,
                'required': True,
                'correct_answer': '46.105.99.163',
                'hint': "Dans l'en-tete IP, 4 octets pour l'IP source."
            },
            'extract_ip_dest': {
                'title': 'Extraire IP Destination',
                'description': 'Trouvez l\'adresse IP de destination',
                'completed': False,
                'required': True,
                'correct_answer': '192.168.4.2',
                'hint': "Apres l'IP source, 4 octets pour l'IP destination."
            },
            'identify_protocol': {
                'title': 'Identifier le Protocole',
                'description': 'Trouvez le protocole de transport utilise',
                'completed': False,
                'required': True,
                'correct_answer': 'TCP',
                'hint': "Le champ Protocol dans l'en-tete IP indique TCP (6) ou UDP (17)."
            },
            'complete_report': {
                'title': 'Completer le Rapport',
                'description': 'Soumettez votre rapport d\'analyse complet',
                'completed': False,
                'required': True,
                'hint': "Remplissez tous les champs du rapport et cliquez Soumettre."
            }
        }

        # Tracking
        self.pcap_analyzer_opened = False

        # Correct answers for validation
        self.correct_answers = {
            "dest_mac": "00:1e:ec:26:d2:ac",
            "src_mac": "26:02:06:49:6b:31",
            "src_ip": "46.105.99.163",
            "dest_ip": "192.168.4.2",
            "packet_length": "66",
            "protocol": "TCP",
            "link_type": "Ethernet",
            "timestamp": "15/06/2024"
        }

    def check_pcap_analyzer_downloaded(self) -> bool:
        """Check if PCAP Analyzer has been downloaded"""
        downloaded_tools = self.profile_data.get('downloaded_tools', [])
        if 'pcap_analyzer' in downloaded_tools:
            self.objectives['download_pcap_analyzer']['completed'] = True
            return True
        return False

    def mark_pcap_analyzer_opened(self):
        """Mark that PCAP Analyzer was opened"""
        if self.check_pcap_analyzer_downloaded():
            self.pcap_analyzer_opened = True
            self.objectives['open_pcap_analyzer']['completed'] = True

    def validate_answer(self, field_key: str, value: str) -> bool:
        """
        Validate a submitted answer

        Args:
            field_key: The field being validated
            value: The submitted value

        Returns:
            True if correct
        """
        if field_key not in self.correct_answers:
            return False

        correct = self.correct_answers[field_key].strip().lower()
        submitted = value.strip().lower()

        # Special handling for MAC addresses
        if field_key in ["dest_mac", "src_mac"]:
            correct = correct.replace("-", ":")
            submitted = submitted.replace("-", ":")

        return submitted == correct

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
        """Get full mission briefing"""
        return {
            'title': 'Mission 3: Analyse de Fichier PCAP',
            'difficulty': 'Avance',
            'estimated_time': '25-35 minutes',
            'description': """
Le Professeur t'a envoye un fichier de capture reseau suspect.

Ce fichier PCAP contient des paquets bruts captures sur un reseau.
Ta mission est d'analyser les donnees hexadecimales pour extraire
les informations critiques.

CONTEXTE:
Un fichier capture_suspect.pcap a ete intercepte. Il contient
des communications entre un serveur externe et une machine
du reseau local. Tu dois identifier les participants.

COMPETENCES REQUISES:
- Comprendre la structure d'un fichier PCAP
- Lire les en-tetes Ethernet et IP en hexadecimal
- Convertir les octets en adresses MAC et IP
- Identifier les protocoles de transport

OUTILS NECESSAIRES:
- Navigateur > Market : Telecharger PCAP Analyzer
- Packet Lab : Lancer PCAP Analyzer
- PCAP Analyzer : Analyser le fichier capture

A EXTRAIRE:
1. Adresse MAC Destination
2. Adresse MAC Source
3. Adresse IP Source
4. Adresse IP Destination
5. Taille du paquet
6. Protocole de transport
7. Type de liaison
8. Timestamp

RECOMPENSES:
- +75 XP
- Badge "Packet Forensics Expert"
- Debloquer Mission 4

Bonne analyse, expert!
            """.strip(),
            'objectives': self.objectives
        }

    def award_completion_rewards(self) -> Dict:
        """Award XP and badges for completing the mission"""
        rewards = {
            'xp': 500,
            'credits': 200,  # +200 dollars credits
            'badges': ['Packet Forensics Expert'],
            'unlocked_missions': ['mission4'],
            'title': 'Mission 3 Terminee!',
            'message': """
Impressionnant, analyste forensique!

Tu as reussi a extraire toutes les informations du fichier PCAP.
Voici ce que tu as decouvert:

ANALYSE DU FICHIER CAPTURE:

Source de la communication:
- MAC: 26:02:06:49:6b:31
- IP: 46.105.99.163 (Serveur externe)

Destination:
- MAC: 00:1e:ec:26:d2:ac
- IP: 192.168.4.2 (Machine locale)

Protocole: TCP sur Ethernet
Taille: 66 octets

Tes competences en analyse forensique sont maintenant confirmees.
Tu peux lire les paquets bruts comme un expert!

RECOMPENSES OBTENUES:
- +500 XP
- +200 Credits
- Reputation: Membre de Confiance (Trusted Member)
- Badge "Packet Forensics Expert"
- Mission 4 debloquee

Tu progresses rapidement!
            """.strip()
        }

        # Update profile
        progress = self.profile_data.get('progress', {})
        progress['xp'] = progress.get('xp', 0) + rewards['xp']
        progress['credits'] = progress.get('credits', 0) + rewards['credits']
        progress['level'] = 'Membre de Confiance'  # Trusted Member
        progress['badges'] = progress.get('badges', [])

        if 'Packet Forensics Expert' not in progress['badges']:
            progress['badges'].append('Packet Forensics Expert')

        progress['missions_completed'] = progress.get('missions_completed', [])
        if 'mission3' not in progress['missions_completed']:
            progress['missions_completed'].append('mission3')

        progress['unlocked_missions'] = progress.get('unlocked_missions', [])
        if 'mission4' not in progress['unlocked_missions']:
            progress['unlocked_missions'].append('mission4')

        return rewards

    def get_hint(self, objective_id: str) -> str:
        """Get hint for specific objective"""
        if objective_id in self.objectives:
            return self.objectives[objective_id].get('hint', "Analysez attentivement le dump hexadecimal.")
        return "Analysez attentivement le dump hexadecimal."
