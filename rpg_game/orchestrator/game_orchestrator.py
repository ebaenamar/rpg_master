from typing import Dict, Any, List, Optional, Tuple
import json
import os

from rpg_game.rag.retriever import RAGRetriever
from rpg_game.scoring.engine import ScoringEngine
from rpg_game.behavior.controller import BehaviorController
from rpg_game.agent.llm_agent import LLMCharacterAgent


class GameOrchestrator:
    """Central controller for the RPG game flow and logic"""
    
    def __init__(self, game_data_path: str = "./data/game_data.json"):
        """Initialize the game orchestrator with all components
        
        Args:
            game_data_path: Path to the game data JSON file
        """
        # Initialize components
        self.rag_retriever = RAGRetriever()
        self.scoring_engine = ScoringEngine()
        self.behavior_controller = BehaviorController()
        # Get API key from environment and pass it explicitly to the agent
        api_key = os.environ.get('AI21_API_KEY')
        self.llm_agent = LLMCharacterAgent(api_key=api_key)
        
        # Game state
        self.current_scene_id = None
        self.scenes = {}
        self.player_name = "Player"
        self.game_state = {
            "visited_scenes": [],
            "inventory": [],
            "quest_progress": {},
            "time_of_day": "morning",
            "current_location": ""
        }
        
        # Load game data
        self._load_game_data(game_data_path)
    
    def _load_game_data(self, game_data_path: str) -> None:
        """Load game scenes and data from JSON file"""
        try:
            if os.path.exists(game_data_path):
                with open(game_data_path, 'r', encoding='utf-8') as f:
                    game_data = json.load(f)
                    
                self.scenes = game_data.get("scenes", {})
                self.current_scene_id = game_data.get("starting_scene", None)
                
                print(f"Loaded {len(self.scenes)} scenes from game data")
            else:
                print(f"Game data file not found at {game_data_path}")
                # Initialize with empty scenes if file doesn't exist
                self.scenes = {}
                self.current_scene_id = None
        except Exception as e:
            print(f"Error loading game data: {e}")
            self.scenes = {}
            self.current_scene_id = None
    
    def start_game(self, player_name: str = "Player") -> Dict[str, Any]:
        """Start a new game
        
        Args:
            player_name: Name of the player character
            
        Returns:
            Initial scene information
        """
        self.player_name = player_name
        
        # Reset game state
        self.game_state = {
            "visited_scenes": [],
            "inventory": [],
            "quest_progress": {},
            "time_of_day": "morning",
            "current_location": ""
        }
        
        # Reset scoring engine
        self.scoring_engine = ScoringEngine()
        
        # Reset behavior controller
        self.behavior_controller = BehaviorController()
        
        # Start with the first scene
        if not self.current_scene_id and self.scenes:
            self.current_scene_id = list(self.scenes.keys())[0]
        
        # Get the initial scene
        return self.get_current_scene()
    
    def get_current_scene(self) -> Dict[str, Any]:
        """Get the current scene information with action choices
        
        Returns:
            Scene information with generated action choices
        """
        if not self.current_scene_id or self.current_scene_id not in self.scenes:
            return {
                "error": "No valid scene available",
                "description": "The game has not been properly initialized."
            }
        
        # Get the current scene
        scene = self.scenes[self.current_scene_id]
        
        # Update game state
        if self.current_scene_id not in self.game_state["visited_scenes"]:
            self.game_state["visited_scenes"].append(self.current_scene_id)
        
        self.game_state["current_location"] = scene.get("location", "")
        
        # Retrieve historical context for the scene
        historical_context = []
        if "rag_context_query" in scene:
            historical_context = self.rag_retriever.retrieve(
                query=scene["rag_context_query"],
                filter_tags=scene.get("rag_filter_tags", None)
            )
        
        # Generate action choices using the LLM agent
        scene_context = {
            "description": scene["description"],
            "location": scene.get("location", ""),
            "time_of_day": self.game_state["time_of_day"]
        }
        
        agent_context = self.behavior_controller.get_prompt_context()
        
        # Generate action choices if they're not predefined
        action_choices = scene.get("actions", [])
        if not action_choices:
            action_choices = self.llm_agent.generate_action_choices(
                agent_context=agent_context,
                scene_context=scene_context,
                historical_context=historical_context
            )
        
        # Prepare the scene response
        scene_response = {
            "scene_id": self.current_scene_id,
            "title": scene.get("title", "Untitled Scene"),
            "description": scene["description"],
            "location": scene.get("location", ""),
            "time_of_day": self.game_state["time_of_day"],
            "actions": action_choices,
            "historical_context": historical_context,
            "player_scores": self.scoring_engine.get_current_scores()
        }
        
        return scene_response
    
    def process_player_action(self, action_index: int, custom_action: Optional[str] = None) -> Dict[str, Any]:
        """Process the player's chosen action
        
        Args:
            action_index: Index of the chosen action (0-3)
            custom_action: Optional custom action text
            
        Returns:
            Result of the action with agent response
        """
        if not self.current_scene_id or self.current_scene_id not in self.scenes:
            return {"error": "No valid scene available"}
        
        # Get the current scene
        scene = self.scenes[self.current_scene_id]
        
        # Get the chosen action
        current_scene = self.get_current_scene()
        actions = current_scene["actions"]
        
        if action_index < 0 or action_index >= len(actions):
            return {"error": "Invalid action index"}
        
        chosen_action = actions[action_index]
        action_description = custom_action if custom_action else chosen_action
        
        # Apply score effects for the action
        score_effects = scene.get("score_effects", {}).get(str(action_index), {})
        if not score_effects:
            # Default minimal effects if none defined
            score_effects = {"xp": 1}
        
        updated_scores = self.scoring_engine.apply_score_effects(
            action_id=f"{self.current_scene_id}_{action_index}",
            effects=score_effects,
            description=action_description
        )
        
        # Update agent behavior based on player action
        self.behavior_controller.update_agent_state(
            player_scores=updated_scores,
            action_description=action_description
        )
        
        # Generate agent response to the player's action
        scene_context = {
            "description": scene["description"],
            "location": scene.get("location", ""),
            "time_of_day": self.game_state["time_of_day"]
        }
        
        agent_context = self.behavior_controller.get_prompt_context()
        
        agent_response = self.llm_agent.generate_response(
            agent_context=agent_context,
            scene_context=scene_context,
            historical_context=current_scene["historical_context"],
            player_message=f"I {action_description}"
        )
        
        # Determine the next scene
        next_scene_id = None
        if "next_scene_map" in scene and str(action_index) in scene["next_scene_map"]:
            next_scene_id = scene["next_scene_map"][str(action_index)]
        
        # Prepare the action result
        action_result = {
            "action_taken": action_description,
            "agent_response": agent_response,
            "updated_scores": updated_scores,
            "has_next_scene": next_scene_id is not None
        }
        
        # Update the current scene if there's a next scene
        if next_scene_id and next_scene_id in self.scenes:
            self.current_scene_id = next_scene_id
        
        return action_result
    
    def advance_to_next_scene(self) -> Dict[str, Any]:
        """Advance to the next scene after player action
        
        Returns:
            Next scene information
        """
        return self.get_current_scene()
    
    def save_game(self, save_path: str = "./data/save_game.json") -> bool:
        """Save the current game state
        
        Args:
            save_path: Path to save the game state
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Prepare save data
            save_data = {
                "player_name": self.player_name,
                "current_scene_id": self.current_scene_id,
                "game_state": self.game_state,
                "alignment": self.scoring_engine.alignment.dict(),
                "action_history": self.scoring_engine.action_history,
                "agent_memory": self.behavior_controller.memory.dict()
            }
            
            # Save to file
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_path: str = "./data/save_game.json") -> bool:
        """Load a saved game state
        
        Args:
            save_path: Path to the saved game state
            
        Returns:
            True if load successful, False otherwise
        """
        try:
            if not os.path.exists(save_path):
                return False
            
            # Load save data
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Restore game state
            self.player_name = save_data.get("player_name", "Player")
            self.current_scene_id = save_data.get("current_scene_id")
            self.game_state = save_data.get("game_state", {})
            
            # Restore scoring engine state
            alignment_data = save_data.get("alignment", {})
            action_history = save_data.get("action_history", [])
            
            self.scoring_engine = ScoringEngine()
            self.scoring_engine.alignment = self.scoring_engine.alignment.__class__(**alignment_data)
            self.scoring_engine.action_history = action_history
            
            # Restore agent memory
            agent_memory_data = save_data.get("agent_memory", {})
            self.behavior_controller = BehaviorController()
            self.behavior_controller.memory = self.behavior_controller.memory.__class__(**agent_memory_data)
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
