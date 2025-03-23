import os
import json
from dotenv import load_dotenv

from rpg_game.orchestrator.game_orchestrator import GameOrchestrator
from rpg_game.rag.retriever import RAGRetriever, load_sample_data

# Load environment variables
load_dotenv()

def setup_rag_system():
    """Set up the RAG system with historical data"""
    print("Setting up RAG system with historical data...")
    
    # Create data directory if it doesn't exist
    os.makedirs("./data/vector_db", exist_ok=True)
    
    # Initialize RAG retriever
    retriever = RAGRetriever()
    
    # Load sample historical data
    historical_data = load_sample_data("./data/historical_data.json")
    
    if historical_data:
        # Add documents to vector database
        retriever.add_documents(historical_data)
        print(f"Added {len(historical_data)} historical documents to RAG system")
    else:
        print("No historical data found or error loading data")
    
    return retriever

def text_based_game_loop():
    """Run a simple text-based version of the game"""
    # Set up RAG system
    setup_rag_system()
    
    # Initialize game orchestrator
    game = GameOrchestrator()
    
    # Start the game
    player_name = input("Enter your character's name: ")
    current_scene = game.start_game(player_name)
    
    print("\n" + "=" * 50)
    print(f"Welcome to Medieval Chronicles: The Fallen Knight, {player_name}!")
    print("You are accompanied by Ser Elyen, a fallen knight seeking redemption.")
    print("=" * 50 + "\n")
    
    # Game loop
    while True:
        # Display current scene
        print(f"\n== {current_scene['title']} ==\n")
        print(current_scene['description'])
        print("\n")
        
        # Display historical context if available
        if current_scene.get('historical_context'):
            print("Historical Context:")
            for item in current_scene['historical_context']:
                print(f"- {item['title']}: {item['text'][:100]}...")
            print("\n")
        
        # Display player alignment
        alignment = current_scene['player_scores']['alignment']
        relationship = current_scene['player_scores']['relationship']
        print(f"Alignment: {alignment['description']} ({alignment['law_chaos']}/{alignment['good_evil']})")
        print(f"Relationship with Ser Elyen: {relationship['description']} ({relationship['trust']}/100)")
        print("\n")
        
        # Display action choices
        print("What will you do?")
        for i, action in enumerate(current_scene['actions']):
            print(f"{chr(65+i)}) {action}")
        
        # Get player choice
        while True:
            choice = input("\nEnter your choice (A, B, C, D): ").upper()
            if choice in ['A', 'B', 'C', 'D']:
                action_index = ord(choice) - ord('A')
                if action_index < len(current_scene['actions']):
                    break
            print("Invalid choice. Please try again.")
        
        # Process player action
        action_result = game.process_player_action(action_index)
        
        # Display agent response
        print("\n" + "-" * 50)
        print(f"Ser Elyen: {action_result['agent_response']}")
        print("-" * 50 + "\n")
        
        # Check if game should continue
        if action_result['has_next_scene']:
            # Advance to next scene
            current_scene = game.advance_to_next_scene()
        else:
            # End of game or branch
            print("\nYou have reached the end of this path.")
            if input("Would you like to save your progress? (y/n): ").lower() == 'y':
                game.save_game()
                print("Game saved.")
            
            if input("Would you like to continue exploring? (y/n): ").lower() != 'y':
                break
            
            # Return to a previous scene for exploration
            current_scene = game.get_current_scene()
    
    print("\nThank you for playing Medieval Chronicles: The Fallen Knight!")

def main():
    """Main entry point"""
    # Check if AI21 API key is set
    if not os.getenv('AI21_API_KEY'):
        print("WARNING: AI21_API_KEY environment variable is not set.")
        print("Please set your AI21 API key in a .env file or environment variable.")
        api_key = input("Enter your AI21 API key to continue: ")
        os.environ['AI21_API_KEY'] = api_key
    
    # Run the game
    text_based_game_loop()

if __name__ == "__main__":
    main()
