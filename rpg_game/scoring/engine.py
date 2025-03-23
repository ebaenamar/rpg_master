from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

from rpg_game.config import INITIAL_ALIGNMENT


class AlignmentScore(BaseModel):
    """Player alignment and relationship scores"""
    law_chaos: int = INITIAL_ALIGNMENT["law_chaos"]  # -100 (Chaotic) to 100 (Lawful)
    good_evil: int = INITIAL_ALIGNMENT["good_evil"]  # -100 (Evil) to 100 (Good)
    trust: int = INITIAL_ALIGNMENT["trust"]  # 0 (No trust) to 100 (Complete trust)
    xp: int = 0
    skills: Dict[str, int] = {}

    def get_alignment_description(self) -> Tuple[str, str]:
        """Get the textual description of the player's alignment"""
        # Law-Chaos axis
        if self.law_chaos >= 70:
            law_desc = "Lawful"
        elif self.law_chaos >= 30:
            law_desc = "Neutral (Lawful leaning)"
        elif self.law_chaos > -30:
            law_desc = "Neutral"
        elif self.law_chaos > -70:
            law_desc = "Neutral (Chaotic leaning)"
        else:
            law_desc = "Chaotic"
            
        # Good-Evil axis
        if self.good_evil >= 70:
            good_desc = "Good"
        elif self.good_evil >= 30:
            good_desc = "Neutral (Good leaning)"
        elif self.good_evil > -30:
            good_desc = "Neutral"
        elif self.good_evil > -70:
            good_desc = "Neutral (Evil leaning)"
        else:
            good_desc = "Evil"
            
        return law_desc, good_desc
    
    def get_trust_description(self) -> str:
        """Get the textual description of the trust level"""
        if self.trust >= 90:
            return "Unwavering Trust"
        elif self.trust >= 70:
            return "Strong Trust"
        elif self.trust >= 50:
            return "Moderate Trust"
        elif self.trust >= 30:
            return "Cautious Trust"
        elif self.trust >= 10:
            return "Suspicious"
        else:
            return "Distrustful"


class ScoringEngine:
    """Engine to track and update player alignment and relationships"""
    
    def __init__(self):
        """Initialize the scoring engine with default alignment"""
        self.alignment = AlignmentScore()
        self.action_history: List[Dict[str, Any]] = []
    
    def apply_score_effects(self, action_id: str, effects: Dict[str, int], description: str = "") -> Dict[str, Any]:
        """Apply score effects based on player action
        
        Args:
            action_id: Identifier for the action
            effects: Dictionary of score effects (law, good, trust, etc.)
            description: Optional description of the action
            
        Returns:
            Updated alignment scores
        """
        # Apply effects to alignment
        if "law" in effects:
            self.alignment.law_chaos = max(-100, min(100, self.alignment.law_chaos + effects["law"]))
        
        if "good" in effects:
            self.alignment.good_evil = max(-100, min(100, self.alignment.good_evil + effects["good"]))
        
        if "trust" in effects:
            self.alignment.trust = max(0, min(100, self.alignment.trust + effects["trust"]))
        
        if "xp" in effects:
            self.alignment.xp += effects["xp"]
        
        # Add skills or update existing ones
        if "skills" in effects and isinstance(effects["skills"], dict):
            for skill, value in effects["skills"].items():
                if skill in self.alignment.skills:
                    self.alignment.skills[skill] += value
                else:
                    self.alignment.skills[skill] = value
        
        # Record action in history
        action_record = {
            "action_id": action_id,
            "description": description,
            "effects": effects,
            "resulting_alignment": self.alignment.dict()
        }
        self.action_history.append(action_record)
        
        return self.get_current_scores()
    
    def get_current_scores(self) -> Dict[str, Any]:
        """Get the current alignment scores with descriptions"""
        law_desc, good_desc = self.alignment.get_alignment_description()
        trust_desc = self.alignment.get_trust_description()
        
        return {
            "alignment": {
                "law_chaos": self.alignment.law_chaos,
                "good_evil": self.alignment.good_evil,
                "description": f"{law_desc} {good_desc}"
            },
            "relationship": {
                "trust": self.alignment.trust,
                "description": trust_desc
            },
            "progression": {
                "xp": self.alignment.xp,
                "skills": self.alignment.skills
            }
        }
    
    def get_action_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the recent action history
        
        Args:
            limit: Number of recent actions to return
            
        Returns:
            List of recent actions with their effects
        """
        return self.action_history[-limit:] if self.action_history else []
