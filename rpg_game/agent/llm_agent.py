from typing import Dict, Any, List, Optional
import json

from ai21 import AI21Client
from ai21.models.chat import ChatMessage

from rpg_game.config import AI21_API_KEY, DEFAULT_MODEL


class LLMCharacterAgent:
    """AI21-powered character agent for the RPG game"""
    
    def __init__(self, api_key: str = AI21_API_KEY, model: str = DEFAULT_MODEL):
        """Initialize the LLM agent with AI21 client
        
        Args:
            api_key: AI21 API key
            model: AI21 model to use
        """
        self.client = AI21Client(api_key=api_key)
        self.model = model
        self.conversation_history: List[ChatMessage] = []
    
    def _build_system_prompt(self, agent_context: Dict[str, Any], scene_context: Dict[str, Any], 
                            historical_context: List[Dict[str, Any]]) -> str:
        """Build the system prompt for the LLM agent
        
        Args:
            agent_context: Agent memory and state
            scene_context: Current scene information
            historical_context: Retrieved historical context from RAG
            
        Returns:
            Formatted system prompt
        """
        # Format historical context
        history_text = ""
        if historical_context:
            history_text = "Historical context:\n"
            for item in historical_context:
                history_text += f"- {item['title']}: {item['text']}\n"
        
        # Format recent actions
        recent_actions = "\n".join([f"- {action}" for action in agent_context["recent_actions"]]) if agent_context["recent_actions"] else "None"
        
        # Build the complete system prompt
        system_prompt = f"""You are {agent_context['name']}, a {agent_context['class']} from the medieval era (year 1312).
        
        Your alignment is {agent_context['alignment']} and your current mood is {agent_context['mood']}.
        
        Backstory: {agent_context['backstory']}
        
        Your trust in the player is {agent_context['trust_in_player']}/100.
        
        Current scene: {scene_context['description']}
        
        Recent events:\n{recent_actions}
        
        {history_text}
        
        Respond in character as {agent_context['name']}. Your responses should reflect your mood, alignment, and trust in the player.
        Keep your responses concise (2-3 sentences) and authentic to medieval speech patterns without being difficult to understand.
        Do not use modern phrases, references, or technology.
        """
        
        return system_prompt
    
    def generate_response(self, agent_context: Dict[str, Any], scene_context: Dict[str, Any], 
                          historical_context: List[Dict[str, Any]], player_message: str) -> str:
        """Generate a response from the LLM agent
        
        Args:
            agent_context: Agent memory and state
            scene_context: Current scene information
            historical_context: Retrieved historical context from RAG
            player_message: Player's message or action
            
        Returns:
            Agent's response
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(agent_context, scene_context, historical_context)
        
        # Create messages array
        messages = [
            ChatMessage(content=system_prompt, role="system")
        ]
        
        # Add conversation history (limited to last 10 exchanges)
        if self.conversation_history:
            messages.extend(self.conversation_history[-10:])
        
        # Add player's current message
        messages.append(ChatMessage(content=player_message, role="user"))
        
        # Generate response from AI21
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=150,
        )
        
        agent_response = response.choices[0].message.content
        
        # Update conversation history
        self.conversation_history.append(ChatMessage(content=player_message, role="user"))
        self.conversation_history.append(ChatMessage(content=agent_response, role="assistant"))
        
        return agent_response
    
    def generate_action_choices(self, agent_context: Dict[str, Any], scene_context: Dict[str, Any], 
                               historical_context: List[Dict[str, Any]]) -> List[str]:
        """Generate four action choices for the player
        
        Args:
            agent_context: Agent memory and state
            scene_context: Current scene information
            historical_context: Retrieved historical context from RAG
            
        Returns:
            List of four action choices
        """
        # Build system prompt for action generation
        system_prompt = f"""You are a medieval RPG game master.
        
        Current scene: {scene_context['description']}
        
        Historical context:
        {json.dumps(historical_context, indent=2)}
        
        Generate EXACTLY 4 possible actions for the player. Each action should:
        1. Be a single sentence starting with a verb
        2. Represent different moral or strategic choices
        3. Be historically plausible for medieval times
        4. Lead to different potential outcomes
        
        Format your response as a JSON array of 4 strings, with no additional text.
        """
        
        # Create messages array
        messages = [
            ChatMessage(content=system_prompt, role="system"),
            ChatMessage(content="Generate 4 action choices for this scene.", role="user")
        ]
        
        # Generate response from AI21
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.8,
            max_tokens=200,
        )
        
        # Parse the response to extract the action choices
        try:
            # Try to parse as JSON
            content = response.choices[0].message.content
            # Clean up the content to ensure it's valid JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            actions = json.loads(content)
            
            # Ensure we have exactly 4 actions
            if len(actions) != 4:
                raise ValueError(f"Expected 4 actions, got {len(actions)}")
                
            return actions
        except Exception as e:
            print(f"Error parsing action choices: {e}")
            # Fallback to default actions if parsing fails
            return [
                f"Investigate the {scene_context.get('location', 'area')} further.",
                f"Ask {agent_context['name']} for advice.",
                "Leave and find another path.",
                "Wait and observe the surroundings."
            ]
    
    def stream_response(self, agent_context: Dict[str, Any], scene_context: Dict[str, Any], 
                       historical_context: List[Dict[str, Any]], player_message: str) -> None:
        """Stream a response from the LLM agent (for real-time display)
        
        Args:
            agent_context: Agent memory and state
            scene_context: Current scene information
            historical_context: Retrieved historical context from RAG
            player_message: Player's message or action
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(agent_context, scene_context, historical_context)
        
        # Create messages array
        messages = [
            ChatMessage(content=system_prompt, role="system")
        ]
        
        # Add conversation history (limited to last 10 exchanges)
        if self.conversation_history:
            messages.extend(self.conversation_history[-10:])
        
        # Add player's current message
        messages.append(ChatMessage(content=player_message, role="user"))
        
        # Generate streaming response from AI21
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.7,
            max_tokens=150,
            stream=True,
        )
        
        # Collect the full response for conversation history
        full_response = ""
        
        # Stream the response
        print(f"\n{agent_context['name']}:", end="")
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        print("\n")
        
        # Update conversation history
        self.conversation_history.append(ChatMessage(content=player_message, role="user"))
        self.conversation_history.append(ChatMessage(content=full_response, role="assistant"))
