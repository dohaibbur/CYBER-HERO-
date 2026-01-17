"""
save_load.py CyberHero - Système de Sauvegarde et Chargement
Gère la persistance des profils de joueurs
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from colorama import Fore, Style


class SaveLoadManager:
    """
    Gère la sauvegarde et le chargement des profils de joueurs
    """
    
    def __init__(self):
        # Use persistent data directory from environment variable
        data_dir = os.environ.get("CYBERHERO_DATA_DIR", ".")
        self.profiles_dir = os.path.join(data_dir, "data", "profiles")
        self._ensure_profiles_directory()
    
    def _ensure_profiles_directory(self):
        """Crée le dossier profiles s'il n'existe pas"""
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
            print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} Dossier de profils créé.")
    
    def _get_profile_filename(self, nickname: str) -> str:
        """
        Génère le nom de fichier pour un profil
        Nettoie le nickname pour éviter les problèmes de système de fichiers
        """
        clean_nickname = "".join(c for c in nickname if c.isalnum() or c in "_-").lower()
        return os.path.join(self.profiles_dir, f"{clean_nickname}_profile.json")
    
    def save_profile(self, profile_data: Dict) -> tuple[bool, str]:
        """
        Sauvegarde un profil de joueur
        
        Args:
            profile_data: Dictionnaire contenant les données du profil
        
        Returns:
            (succès: bool, message: str)
        """
        try:
            # Ajouter des métadonnées
            profile_data["saved_at"] = datetime.now().isoformat()
            
            if "created_at" not in profile_data:
                profile_data["created_at"] = datetime.now().isoformat()
            
            # Initialiser la progression si elle n'existe pas
            if "progress" not in profile_data:
                profile_data["progress"] = {
                    "current_stage": "profile_created",
                    "stages_completed": ["profile_creation"],
                    "missions_completed": [],
                    "current_mission": None
                }
            
            # Sauvegarder dans un fichier JSON
            filename = self._get_profile_filename(profile_data["nickname"])
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4, ensure_ascii=False)
            
            return True, f"Profil '{profile_data['nickname']}' sauvegardé avec succès."
        
        except Exception as e:
            return False, f"Erreur lors de la sauvegarde: {str(e)}"
    
    def load_profile(self, nickname: str) -> Optional[Dict]:
        """
        Charge un profil de joueur
        
        Args:
            nickname: Le pseudonyme du joueur
        
        Returns:
            Dictionnaire du profil ou None si non trouvé
        """
        try:
            filename = self._get_profile_filename(nickname)
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            return profile_data
        
        except Exception as e:
            print(f"{Fore.RED}[ERREUR]{Style.RESET_ALL} Erreur lors du chargement: {e}")
            return None
    
    def list_profiles(self) -> List[Dict]:
        """
        Liste tous les profils disponibles
        
        Returns:
            Liste de dictionnaires avec infos basiques des profils
        """
        profiles = []
        
        try:
            if not os.path.exists(self.profiles_dir):
                return profiles
            
            for filename in os.listdir(self.profiles_dir):
                if filename.endswith("_profile.json"):
                    filepath = os.path.join(self.profiles_dir, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            profile_data = json.load(f)
                        
                        # Extraire les infos essentielles
                        profile_info = {
                            "nickname": profile_data.get("nickname", "Unknown"),
                            "hacker_type": profile_data.get("hacker_type", "unknown"),
                            "created_at": profile_data.get("created_at", "Unknown"),
                            "saved_at": profile_data.get("saved_at", "Unknown"),
                            "current_stage": profile_data.get("progress", {}).get("current_stage", "unknown"),
                            "filename": filename
                        }
                        
                        profiles.append(profile_info)
                    
                    except Exception as e:
                        print(f"{Fore.YELLOW}[AVERTISSEMENT]{Style.RESET_ALL} Impossible de lire {filename}: {e}")
            
            # Trier par date de sauvegarde (plus récent en premier)
            profiles.sort(key=lambda x: x["saved_at"], reverse=True)
        
        except Exception as e:
            print(f"{Fore.RED}[ERREUR]{Style.RESET_ALL} Erreur lors de la liste des profils: {e}")
        
        return profiles
    
    def delete_profile(self, nickname: str) -> tuple[bool, str]:
        """
        Supprime un profil de joueur
        
        Args:
            nickname: Le pseudonyme du profil à supprimer
        
        Returns:
            (succès: bool, message: str)
        """
        try:
            filename = self._get_profile_filename(nickname)
            
            if not os.path.exists(filename):
                return False, f"Le profil '{nickname}' n'existe pas."
            
            os.remove(filename)
            return True, f"Profil '{nickname}' supprimé avec succès."
        
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    def profile_exists(self, nickname: str) -> bool:
        """
        Vérifie si un profil existe
        
        Args:
            nickname: Le pseudonyme à vérifier
        
        Returns:
            True si le profil existe, False sinon
        """
        filename = self._get_profile_filename(nickname)
        return os.path.exists(filename)


class ProfileManagerView:
    """
    Interface de gestion des profils (Liste, Charger, Supprimer)
    """
    
    def __init__(self):
        self.manager = SaveLoadManager()
    
    def clear_screen(self):
        """Efface l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Affiche un en-tête stylisé"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{title.center(70)}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
    
    def display_profiles(self, profiles: List[Dict]):
        """
        Affiche la liste des profils de manière stylisée
        """
        if not profiles:
            print(f"{Fore.YELLOW}Aucun profil trouvé.{Style.RESET_ALL}\n")
            return
        
        print(f"{Fore.CYAN}╔{'═'*68}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {'#':<3} {'Pseudonyme':<20} {'Type':<15} {'Dernière sauvegarde':<25} {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═'*68}╣{Style.RESET_ALL}")
        
        for idx, profile in enumerate(profiles, 1):
            nickname = profile["nickname"][:20]
            
            # Couleur selon le type de hacker
            type_colors = {
                "white_hat": Fore.GREEN,
                "grey_hat": Fore.YELLOW,
                "black_hat": Fore.RED
            }
            type_color = type_colors.get(profile["hacker_type"], Fore.WHITE)
            hacker_type = profile["hacker_type"].replace("_", " ").title()[:15]
            
            # Formater la date
            try:
                saved_date = datetime.fromisoformat(profile["saved_at"])
                date_str = saved_date.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = "Date inconnue"
            
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{idx:<3}{Style.RESET_ALL} "
                  f"{Fore.WHITE}{nickname:<20}{Style.RESET_ALL} "
                  f"{type_color}{hacker_type:<15}{Style.RESET_ALL} "
                  f"{Fore.WHITE}{date_str:<25}{Style.RESET_ALL} "
                  f"{Fore.CYAN}║{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}╚{'═'*68}╝{Style.RESET_ALL}\n")
    
    def show_profile_menu(self) -> Optional[Dict]:
        """
        Affiche le menu de gestion des profils
        Permet de charger ou supprimer un profil
        
        Returns:
            Profil chargé ou None
        """
        while True:
            self.clear_screen()
            self.print_header("📂 GESTION DES PROFILS")
            
            profiles = self.manager.list_profiles()
            self.display_profiles(profiles)
            
            if not profiles:
                print(f"{Fore.YELLOW}Aucun profil sauvegardé.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Créez un nouveau profil depuis le menu principal.{Style.RESET_ALL}\n")
                input(f"{Fore.YELLOW}Appuyez sur Entrée pour retourner au menu...{Style.RESET_ALL}")
                return None
            
            print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[Numéro]{Style.RESET_ALL} - Charger le profil")
            print(f"{Fore.RED}[D + Numéro]{Style.RESET_ALL} - Supprimer le profil (ex: D1)")
            print(f"{Fore.YELLOW}[R]{Style.RESET_ALL} - Rafraîchir la liste")
            print(f"{Fore.YELLOW}[Q]{Style.RESET_ALL} - Retour au menu principal\n")
            
            choice = input(f"{Fore.GREEN}Votre choix >>> {Style.RESET_ALL}").strip().upper()
            
            # Retour au menu
            if choice == "Q":
                return None
            
            # Rafraîchir
            if choice == "R":
                continue
            
            # Supprimer un profil
            if choice.startswith("D") and len(choice) > 1:
                try:
                    profile_num = int(choice[1:])
                    
                    if 1 <= profile_num <= len(profiles):
                        profile_to_delete = profiles[profile_num - 1]
                        
                        # Confirmation
                        print(f"\n{Fore.RED}⚠️  ATTENTION: Vous êtes sur le point de supprimer le profil "
                              f"'{profile_to_delete['nickname']}'.{Style.RESET_ALL}")
                        confirm = input(f"{Fore.YELLOW}Confirmer la suppression? (oui/non) >>> {Style.RESET_ALL}").strip().lower()
                        
                        if confirm in ["oui", "o", "yes", "y"]:
                            success, message = self.manager.delete_profile(profile_to_delete["nickname"])
                            
                            if success:
                                print(f"\n{Fore.GREEN}[OK] {message}{Style.RESET_ALL}")
                            else:
                                print(f"\n{Fore.RED}[X] {message}{Style.RESET_ALL}")
                        else:
                            print(f"\n{Fore.YELLOW}Suppression annulée.{Style.RESET_ALL}")
                        
                        input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.RED}[X] Numéro de profil invalide.{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
                
                except ValueError:
                    print(f"\n{Fore.RED}[X] Commande invalide.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
            
            # Charger un profil
            else:
                try:
                    profile_num = int(choice)
                    
                    if 1 <= profile_num <= len(profiles):
                        profile_info = profiles[profile_num - 1]
                        profile_data = self.manager.load_profile(profile_info["nickname"])
                        
                        if profile_data:
                            print(f"\n{Fore.GREEN}[OK] Profil '{profile_info['nickname']}' chargé avec succès!{Style.RESET_ALL}")
                            input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
                            return profile_data
                        else:
                            print(f"\n{Fore.RED}[X] Erreur lors du chargement du profil.{Style.RESET_ALL}")
                            input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.RED}[X] Numéro de profil invalide.{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
                
                except ValueError:
                    print(f"\n{Fore.RED}[X] Entrée invalide. Entrez un numéro, D+numéro, R ou Q.{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")


# Test du module
if __name__ == "__main__":
    from colorama import init
    init(autoreset=True)
    
    # Test: créer et sauvegarder un profil de test
    manager = SaveLoadManager()
    
    test_profile = {
        "nickname": "TestHacker",
        "hacker_type": "white_hat",
        "bio": "Profil de test",
        "avatar_id": 1,
        "completed": True
    }
    
    success, msg = manager.save_profile(test_profile)
    print(f"{Fore.GREEN if success else Fore.RED}{msg}{Style.RESET_ALL}")
    
    # Test: lister les profils
    print(f"\n{Fore.CYAN}Profils disponibles:{Style.RESET_ALL}")
    profiles = manager.list_profiles()
    for p in profiles:
        print(f"  - {p['nickname']} ({p['hacker_type']})")
    
    # Test: interface de gestion
    view = ProfileManagerView()
    loaded_profile = view.show_profile_menu()
    
    if loaded_profile:
        print(f"\n{Fore.GREEN}Profil chargé:{Style.RESET_ALL}")
        print(json.dumps(loaded_profile, indent=2))