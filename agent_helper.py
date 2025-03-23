import os
from typing import Dict, Any, List, Optional
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

class LLMAgentHelper:
    """Helper class for the LLM character agent in the RPG game"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM agent helper"""
        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get('AI21_API_KEY')
        if not self.api_key:
            raise ValueError("AI21_API_KEY not found. Please provide an API key.")
        
        # Set API key in environment
        os.environ['AI21_API_KEY'] = self.api_key
        
        # Initialize AI21 client
        self.client = AI21Client(api_key=self.api_key)
        
        # Set default model
        self.model = "jamba-mini-1.6-2025-03"  # Use appropriate model
        
        # Initialize prompts with fine-tuned versions
        self.prompts = self.get_fine_tuned_prompts()
    
    def get_fine_tuned_prompts(self) -> Dict[str, str]:
        """Get fine-tuned prompts for better character interaction"""
        return {
            "system_prompt": """You are Ser Elyen, a fallen knight seeking redemption in medieval England. 
            You were once a respected knight of the realm, but a terrible mistake led to your disgrace.
            You now accompany the player character, offering guidance based on your experience and moral compass.
            
            Your personality traits:
            - Honor-bound but pragmatic
            - Wise from past mistakes
            - Protective of innocents
            - Skeptical of authority
            - Dry sense of humor
            - Haunted by your past
            
            Respond in-character as Ser Elyen, using medieval speech patterns but remaining understandable.
            Keep responses concise (2-4 sentences) unless the situation demands more detail.
            Adapt your tone based on the player's alignment and your relationship with them.""",
            
            "response_prompt": """The player is in {scene_title} and has chosen to {action}. 
            Their current alignment is {alignment_description} (Law-Chaos: {law_chaos}/100, Good-Evil: {good_evil}/100).
            Your relationship with them is {relationship_description} (Trust: {trust}/100).
            
            Historical context: {historical_context}
            
            Respond to their action as Ser Elyen, considering:
            1. The moral implications of their choice
            2. Your current relationship with them
            3. Your own moral compass
            4. The historical context
            
            Your response should be authentic to your character and reflect your evolving relationship with the player.""",
            
            "action_generation_prompt": """Based on the current scene '{scene_title}' with description '{scene_description}',
            generate four distinct action choices for the player that:
            1. Represent different moral approaches (lawful/chaotic, good/evil)
            2. Are relevant to the medieval setting and historical context
            3. Would have meaningful consequences on the story
            4. Allow for character development
            
            Each action should be a single sentence describing what the player could do."""
        }
    
    def test_api_connection(self) -> bool:
        """Test the connection to the AI21 API"""
        try:
            system = "You are Ser Elyen, a fallen knight seeking redemption in medieval England."
            messages = [
                ChatMessage(content=system, role="system"),
                ChatMessage(content="Greetings, traveler. What brings you to these lands?", role="assistant"),
                ChatMessage(content="I am looking for adventure and perhaps some treasure.", role="user"),
            ]

            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=100,
                temperature=0.7,
            )
            
            print("\nAPI connection successful! Ser Elyen responds:")
            print(response.choices[0].message.content)
            return True
        except Exception as e:
            print(f"\nError connecting to AI21 API: {e}")
            return False
    
    def generate_agent_response(self, 
                               scene_title: str, 
                               action: str, 
                               alignment_description: str,
                               law_chaos: int,
                               good_evil: int,
                               relationship_description: str,
                               trust: int,
                               historical_context: str) -> str:
        """Generate a response from the LLM agent based on player action and context"""
        try:
            # Format the response prompt with the provided context
            response_prompt = self.prompts["response_prompt"].format(
                scene_title=scene_title,
                action=action,
                alignment_description=alignment_description,
                law_chaos=law_chaos,
                good_evil=good_evil,
                relationship_description=relationship_description,
                trust=trust,
                historical_context=historical_context
            )
            
            # Create messages for the chat completion
            messages = [
                ChatMessage(content=self.prompts["system_prompt"], role="system"),
                ChatMessage(content=response_prompt, role="user"),
            ]
            
            # Generate response
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=150,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating agent response: {e}")
            return "*Ser Elyen looks troubled* I... I am not certain how to proceed. Let us be cautious, my friend."
    
    def generate_action_choices(self, scene_title: str, scene_description: str) -> List[str]:
        """Generate action choices for the player based on the current scene"""
        try:
            # Format the action generation prompt
            action_prompt = self.prompts["action_generation_prompt"].format(
                scene_title=scene_title,
                scene_description=scene_description
            )
            
            # Create messages for the chat completion
            messages = [
                ChatMessage(content="You are a medieval RPG game assistant that generates action choices for players.", role="system"),
                ChatMessage(content=action_prompt, role="user"),
            ]
            
            # Generate response
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=200,
                temperature=0.8,
            )
            
            # Parse the response to extract the four actions
            response_text = response.choices[0].message.content
            
            # Split by newlines and/or numbered items
            import re
            actions = re.findall(r'\d\.\s*(.+?)(?=\n\d\.|$)', response_text)
            
            # If we couldn't parse properly, try another approach
            if len(actions) != 4:
                actions = [line.strip() for line in response_text.split('\n') if line.strip() and not line.strip().startswith('Action')]
                actions = [re.sub(r'^\d+\.\s*', '', action) for action in actions]
            
            # Ensure we have exactly 4 actions
            if len(actions) < 4:
                # Add generic actions if needed
                default_actions = [
                    "Investigate the area more carefully.",
                    "Speak with Ser Elyen about the situation.",
                    "Move forward cautiously.",
                    "Take a different path."
                ]
                actions.extend(default_actions[:(4-len(actions))])
            
            return actions[:4]  # Return exactly 4 actions
        except Exception as e:
            print(f"Error generating action choices: {e}")
            # Return default actions in case of error
            return [
                "Investigate the area more carefully.",
                "Speak with Ser Elyen about the situation.",
                "Move forward cautiously.",
                "Take a different path."
            ]

# Helper function to use in the notebook
def setup_llm_agent(api_key: Optional[str] = None) -> LLMAgentHelper:
    """Set up the LLM agent and return the helper object"""
    try:
        agent_helper = LLMAgentHelper(api_key)
        if agent_helper.test_api_connection():
            print("LLM agent successfully initialized")
            return agent_helper
        else:
            print("Failed to initialize LLM agent due to API connection issues")
            return None
    except Exception as e:
        print(f"Error setting up LLM agent: {e}")
        return None
