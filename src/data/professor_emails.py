"""
Professor Emails Data
Contains the content of emails sent by Le Professeur
"""

def get_welcome_email(player_name):
    """Return the welcome email (Mission 1 start)"""
    return {
        "id": "prof_001_welcome",
        "sender": "Le Professeur",
        "subject": "Mission 1: Reconnaissance Reseau",
        "body": f"""Bienvenue dans le programme, {player_name}.

CONTEXTE :
Ta premiere mission est de faire une reconnaissance complete de ton reseau local. Il est crucial de comprendre l'environnement dans lequel tu operes avant de tenter quoi que ce soit.

OBJECTIFS PEDAGOGIQUES :
Tu vas apprendre a :
- Utiliser le terminal de commande.
- Identifier les adresses IP et MAC.
- Comprendre la structure d'un reseau local.

N'oublie pas de personnaliser ton profil sur le forum.

Voici les etapes a suivre pour ta premiere mission :
1. Retourne sur ton bureau.
2. Ouvre le TERMINAL.
3. Execute les commandes pour explorer le reseau. Tape 'help' pour apprendre les commandes disponibles.
4. Tu verras un bouton 'RAPPORT'. Clique dessus pour voir les champs ou tu devras entrer les informations demandees.
5. Une fois que tu as rempli toutes les informations, clique sur ENVOYER.

Elles arriveront dans ma boite de reception. J'attends. Bonne chance.

- Le Professeur""",
        "mission_id": "mission1",
        "attachments": ["network_diagram.txt"],
        "read": False
    }

def get_mission1_success_email(player_name):
    """Return the Mission 1 success email"""
    return {
        "id": "prof_002_m1_success",
        "sender": "Le Professeur",
        "subject": "RE: Mission 1 - Rapport recu",
        "body": f"""Bon travail, {player_name}.

Ton rapport de reconnaissance reseau est exact. Tu as identifie correctement les elements cles de ton environnement.

J'ai credite ton compte de 100 Credits et t'ai attribue le badge 'Network Scout'.

Prepare-toi pour la suite. Les choses vont se compliquer.

- Le Professeur""",
        "mission_id": None,
        "attachments": [],
        "read": False
    }

def get_mission2_email(player_name):
    """Return the Mission 2 briefing email"""
    return {
        "id": "prof_003_mission2",
        "sender": "Le Professeur",
        "subject": "Mission 2: Analyse de Paquets et Detection d'Intrusion",
        "body": f"""Excellent travail sur la Mission 1, {player_name}.

CONTEXTE :
Un intrus s'est infiltre dans notre reseau. J'ai besoin que tu analyses le trafic capture pour l'identifier. La surveillance reseau est la cle de la defense.

OBJECTIFS PEDAGOGIQUES :
Tu vas apprendre a :
- Analyser des paquets reseau avec Wireshark.
- Detecter des scans de ports et des activites suspectes.
- Identifier une machine compromise ou un attaquant.

Voici les etapes a suivre :
1. Va sur le Navigateur, onglet Market, et telecharge 'Wireshark'.
2. Retourne sur le bureau et ouvre l'application 'Net Scanner'.
3. Lance l'outil Wireshark.
4. Analyse le trafic pour trouver l'intrus.
5. Clique sur le bouton 'RAPPORT' pour voir les champs a remplir.
6. Entre les informations demandees et clique sur ENVOYER.

J'attends ton rapport. Bonne chance.

- Le Professeur""",
        "mission_id": "mission2",
        "attachments": ["capture_reseau.pcap"],
        "read": False
    }

def get_mission3_email(player_name):
    """Return the Mission 3 briefing email"""
    return {
        "id": "prof_004_mission3",
        "sender": "Le Professeur",
        "subject": "Mission 3: Analyse de Fichier PCAP",
        "body": f"""Tu progresses bien, {player_name}.

CONTEXTE :
Cette fois, on passe a l'analyse forensique. J'ai intercepte un fichier PCAP brut d'une communication suspecte. Tu dois aller plus loin que la simple interface graphique.

OBJECTIFS PEDAGOGIQUES :
Tu vas apprendre a :
- Lire un dump hexadecimal brut.
- Extraire manuellement des en-tetes Ethernet et IP.
- Comprendre la structure binaire des protocoles reseau.

Voici les etapes a suivre :
1. Va sur le Navigateur, onglet Market, et telecharge 'PCAP Analyzer'.
2. Retourne sur le bureau et ouvre l'application 'Packet Lab'.
3. Lance l'outil PCAP Analyzer.
4. Analyse le dump hexadecimal.
5. Clique sur le bouton 'RAPPORT' pour voir les informations a extraire.
6. Remplis le formulaire et clique sur ENVOYER.

C'est le moment de prouver ta valeur. Bonne chance.

- Le Professeur""",
        "mission_id": "mission3",
        "attachments": ["suspicious_packet.pcap"],
        "read": False
    }