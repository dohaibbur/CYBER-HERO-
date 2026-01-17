import json
import os
from typing import Dict, Optional, List

class MissionManager:
    """Manages mission loading, state, and progression"""
    
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.current_mission = None
        self.mission_state = {}
        
    def load_mission(self, mission_id: str) -> Optional[Dict]:
        """Load a specific mission configuration"""
        missions_dir = "data/missions"
        
        if not os.path.exists(missions_dir):
            print(f"[WARNING] Missions directory not found: {missions_dir}")
            return None
        
        for filename in os.listdir(missions_dir):
            if filename.endswith("_config.json"):
                filepath = os.path.join(missions_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        mission = json.load(f)
                        if mission.get('id') == mission_id:
                            self.current_mission = mission
                            self.mission_state = {
                                'objectives_completed': [],
                                'hints_used': 0,
                                'start_time': None,
                                'attempts': 0
                            }
                            return mission
                except Exception as e:
                    print(f"Error loading mission {mission_id}: {e}")
        
        return None
    
    def complete_objective(self, objective_id: str) -> bool:
        """Mark an objective as completed"""
        if objective_id not in self.mission_state['objectives_completed']:
            self.mission_state['objectives_completed'].append(objective_id)
            return True
        return False
    
    def is_mission_complete(self) -> bool:
        """Check if all objectives are completed"""
        if not self.current_mission:
            return False
            
        total_objectives = len(self.current_mission.get('objectives', []))
        completed = len(self.mission_state['objectives_completed'])
        
        return completed >= total_objectives
    
    def complete_mission(self) -> Dict:
        """Complete the current mission and award rewards"""
        if not self.current_mission:
            return {}
        
        rewards = self.current_mission.get('rewards', {})
        mission_id = self.current_mission['id']
        
        # Update profile
        profile = self.profile_manager.get_current_profile()
        if profile:
            # Add XP
            current_xp = profile.get('xp', 0)
            profile['xp'] = current_xp + rewards.get('xp', 0)
            
            # Mark as completed
            if 'completed_missions' not in profile:
                profile['completed_missions'] = []
            
            if mission_id not in profile['completed_missions']:
                profile['completed_missions'].append(mission_id)
            
            # Unlock new missions
            unlocks = rewards.get('unlocks', [])
            if 'unlocked_missions' not in profile:
                profile['unlocked_missions'] = []
            
            for unlock in unlocks:
                if unlock not in profile['unlocked_missions']:
                    profile['unlocked_missions'].append(unlock)
            
            # Save profile
            self.profile_manager.save_profile(profile)
        
        return rewards
    
    def get_mission_progress(self) -> Dict:
        """Get current mission progress"""
        if not self.current_mission:
            return {}
        
        total = len(self.current_mission.get('objectives', []))
        completed = len(self.mission_state['objectives_completed'])
        
        return {
            'total_objectives': total,
            'completed_objectives': completed,
            'progress_percent': (completed / total * 100) if total > 0 else 0,
            'hints_used': self.mission_state['hints_used']
        }
    
    def use_hint(self) -> Optional[str]:
        """Get next available hint"""
        if not self.current_mission:
            return None
        
        hints = self.current_mission.get('hints', [])
        hint_index = self.mission_state['hints_used']
        
        if hint_index < len(hints):
            self.mission_state['hints_used'] += 1
            return hints[hint_index]
        
        return None