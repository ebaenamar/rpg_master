import os
import json
from typing import Dict, Any, List, Optional

# Import AI21 libraries
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

# Set your API key here
AI21_API_KEY = "your_api_key_here"  # Replace with your actual API key
os.environ['AI21_API_KEY'] = AI21_API_KEY

print("Welcome to Medieval Chronicles: The Fallen Knight!")
print("This is a simplified version of the game to test your AI21 API key.")

# Initialize AI21 client
client = AI21Client(api_key=AI21_API_KEY)

# Test the API connection
def test_api_connection():
    try:
        system = "You are Ser Elyen, a fallen knight seeking redemption in medieval England."
        messages = [
            ChatMessage(content=system, role="system"),
            ChatMessage(content="Greetings, traveler. What brings you to these lands?", role="assistant"),
            ChatMessage(content="I am looking for adventure and perhaps some treasure.", role="user"),
        ]

        response = client.chat.completions.create(
            messages=messages,
            model="jamba-mini-1.6-2025-03",
            max_tokens=100,
            temperature=0.7,
        )
        
        print("\nAPI connection successful! Ser Elyen responds:")
        print(response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"\nError connecting to AI21 API: {e}")
        return False

# Load sample game data
def load_sample_data():
    # Sample scene data
    scene = {
        "title": "The Broken Bell",
        "description": "You stand beneath the broken bell of the village church. The wooden beams creak above you, and dust motes dance in the rays of sunlight streaming through the stained glass windows. The bell's rope hangs limply, frayed at the end.",
        "actions": [
            "Pull the rope to test the bell",
            "Examine the inscription on the bell",
            "Search the altar for clues",
            "Leave quietly and investigate the woods"
        ]
    }
    
    print(f"\n== {scene['title']} ==\n")
    print(scene['description'])
    print("\nWhat will you do?")
    for i, action in enumerate(scene['actions']):
        print(f"{chr(65+i)}) {action}")
    
    return scene

# Simple game interaction
def play_sample_scene(scene):
    # Get player choice
    choice = input("\nEnter your choice (A, B, C, D): ").upper()
    if choice not in ['A', 'B', 'C', 'D']:
        print("Invalid choice. Defaulting to A.")
        choice = 'A'
    
    action_index = ord(choice) - ord('A')
    chosen_action = scene['actions'][action_index]
    
    print(f"\nYou decide to {chosen_action.lower()}.")
    
    # Generate response from Ser Elyen
    try:
        system = "You are Ser Elyen, a fallen knight seeking redemption in medieval England. You are accompanying the player on their quest. Respond to their action in character as a medieval knight. Keep your response brief (2-3 sentences)."
        messages = [
            ChatMessage(content=system, role="system"),
            ChatMessage(content=f"The player is in a village church with a broken bell. They decide to {chosen_action.lower()}.", role="user"),
        ]

        response = client.chat.completions.create(
            messages=messages,
            model="jamba-mini-1.6-2025-03",
            max_tokens=100,
            temperature=0.7,
        )
        
        print("\nSer Elyen:", response.choices[0].message.content)
    except Exception as e:
        print(f"\nError generating response: {e}")
        print("\nSer Elyen: *looks concerned* We should proceed with caution, my friend.")

# Main function
def main():
    # Test API connection
    if test_api_connection():
        # Load sample scene
        scene = load_sample_data()
        
        # Play sample scene
        play_sample_scene(scene)
        
        print("\nThis is just a simple test of the AI21 integration.")
        print("To play the full game, run the main.py file after activating the virtual environment:")
        print("source rpg_venv/bin/activate && python main.py")
    else:
        print("\nPlease check your AI21 API key and try again.")

if __name__ == "__main__":
    main()
