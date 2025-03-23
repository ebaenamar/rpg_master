import os
import sys

def set_api_key():
    print("Setting up AI21 API key for the RPG game")
    
    # Check if API key is already set
    current_key = os.environ.get('AI21_API_KEY')
    if current_key and current_key != "your_api_key_here":
        print(f"✅ AI21_API_KEY is already set in environment variables.")
        return True
    
    # Ask for API key
    api_key = input("Enter your AI21 API key: ")
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return False
    
    # Set the API key in environment
    os.environ['AI21_API_KEY'] = api_key
    print("✅ API key set successfully in environment variables.")
    
    # Also update the rpg_game_starter.py file
    try:
        with open('rpg_game_starter.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder with the actual API key
        updated_content = content.replace(
            'AI21_API_KEY = "your_api_key_here"', 
            f'AI21_API_KEY = "{api_key}"'
        )
        
        with open('rpg_game_starter.py', 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated API key in rpg_game_starter.py")
    except Exception as e:
        print(f"⚠️ Could not update rpg_game_starter.py: {e}")
    
    return True

if __name__ == "__main__":
    success = set_api_key()
    if success:
        print("\nYou can now run the game with:")
        print("python main.py")
    else:
        print("\nAPI key setup failed. Please try again.")
        sys.exit(1)
