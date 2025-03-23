from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from rpg_game.config import DEFAULT_AGENT


class AgentMemory(BaseModel):
    """Memory and state of the LLM agent"""
    name: str = DEFAULT_AGENT["name"]
    character_class: str = DEFAULT_AGENT["class"]
    alignment: str = DEFAULT_AGENT["alignment"]
    backstory: str = DEFAULT_AGENT["backstory"]
    mood: str = "neutral"
    trust_in_player: int = 50
    recent_actions: List[str] = []
    knowledge: Dict[str, Any] = {}


class BehaviorController:
    """Controller for LLM agent behavior and personality"""
    
    def __init__(self):
        """Initialize the behavior controller with default agent memory"""
        self.memory = AgentMemory()
    
    def update_agent_state(self, player_scores: Dict[str, Any], action_description: str) -> None:
        """Update the agent's state based on player scores and recent action
        
        Args:
            player_scores: Current player alignment and relationship scores
            action_description: Description of the player's recent action
        """
        # Update trust based on player relationship score
        self.memory.trust_in_player = player_scores["relationship"]["trust"]
        
        # Update mood based on player's recent action and alignment
        self._update_mood(player_scores, action_description)
        
        # Add action to recent actions list (keep last 5)
        self.memory.recent_actions.append(action_description)
        if len(self.memory.recent_actions) > 5:
            self.memory.recent_actions.pop(0)
    
    def _update_mood(self, player_scores: Dict[str, Any], action_description: str) -> None:
        """Update the agent's mood based on player scores and action"""
        # This is a simplified mood system - in a full game, this would be more complex
        law_chaos = player_scores["alignment"]["law_chaos"]
        good_evil = player_scores["alignment"]["good_evil"]
        trust = player_scores["relationship"]["trust"]
        
        # Determine mood based on alignment and trust
        if trust >= 70:
            if good_evil >= 30:
                self.memory.mood = "friendly"
            elif good_evil <= -30:
                self.memory.mood = "concerned"
            else:
                self.memory.mood = "respectful"
        elif trust >= 40:
            if law_chaos >= 30:
                self.memory.mood = "formal"
            elif law_chaos <= -30:
                self.memory.mood = "cautious"
            else:
                self.memory.mood = "neutral"
        else:
            if good_evil <= -50:
                self.memory.mood = "distrustful"
            else:
                self.memory.mood = "distant"
    
    def add_knowledge(self, key: str, value: Any) -> None:
        """Add knowledge to the agent's memory
        
        Args:
            key: Knowledge identifier
            value: Knowledge content
        """
        self.memory.knowledge[key] = value
    
    def get_prompt_context(self) -> Dict[str, Any]:
        """Get the agent's context for LLM prompting
        
        Returns:
            Dictionary with agent memory and state for prompt construction
        """
        return {
            "name": self.memory.name,
            "class": self.memory.character_class,
            "alignment": self.memory.alignment,
            "backstory": self.memory.backstory,
            "mood": self.memory.mood,
            "trust_in_player": self.memory.trust_in_player,
            "recent_actions": self.memory.recent_actions,
            "knowledge": self.memory.knowledge
        }
