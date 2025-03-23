import os
import sys
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

def set_and_test_ai21_key():
    print("\n" + "=" * 60)
    print("AI21 API Key Setup and Test")
    print("=" * 60)
    
    # Get current API key if set
    current_key = os.environ.get('AI21_API_KEY')
    if current_key and current_key != "your_api_key_here":
        print(f"Current API key found in environment: {current_key[:5]}...{current_key[-5:]}")
        use_current = input("Use this key? (y/n): ").lower().strip() == 'y'
        if use_current:
            api_key = current_key
        else:
            api_key = input("Enter your AI21 API key: ").strip()
    else:
        api_key = input("Enter your AI21 API key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided. Exiting.")
        return False
    
    # Set the API key in environment
    os.environ['AI21_API_KEY'] = api_key
    print("\n✅ API key set in environment variables.")
    
    # Update rpg_game_starter.py
    try:
        with open('rpg_game_starter.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder with the actual API key
        if 'AI21_API_KEY = "your_api_key_here"' in content:
            updated_content = content.replace(
                'AI21_API_KEY = "your_api_key_here"', 
                f'AI21_API_KEY = "{api_key}"'
            )
            
            with open('rpg_game_starter.py', 'w') as f:
                f.write(updated_content)
            
            print("✅ Updated API key in rpg_game_starter.py")
    except Exception as e:
        print(f"⚠️ Could not update rpg_game_starter.py: {e}")
    
    # Test the API connection
    print("\nTesting API connection...")
    try:
        client = AI21Client(api_key=api_key)
        
        # Simple test message
        messages = [
            ChatMessage(content="Hello, can you hear me?", role="user")
        ]
        
        response = client.chat.completions.create(
            messages=messages,
            model="jamba-mini-1.6-2025-03",  # Using the same model as in the config file
            max_tokens=20,
            temperature=0.7,
        )
        
        # Check if we got a valid response
        if response and response.choices and response.choices[0].message.content:
            print("\n✅ API test successful! Response:")
            print(f"AI: {response.choices[0].message.content}")
            print("\nYour API key is working correctly.")
            return True
        else:
            print("\n❌ API test failed: Received empty response")
            return False
            
    except Exception as e:
        print(f"\n❌ API test failed: {str(e)}")
        print("\nPlease check your API key and try again.")
        return False

# For Jupyter notebook
print("Add this code to your Jupyter notebook:")
print("\n" + "=" * 80 + "\n")
print("# Set and test your AI21 API key")
print("from set_ai21_key import set_and_test_ai21_key")
print("success = set_and_test_ai21_key()")
print("# Only continue if the API key test was successful")
print("if success:")
print("    # Now you can run the game")
print("    main()")
print("\n" + "=" * 80 + "\n")

# For command line
if __name__ == "__main__":
    success = set_and_test_ai21_key()
    if success:
        print("\nYou can now run the game with:")
        print("python main.py")
    else:
        print("\nAPI key setup failed. Please try again.")
        sys.exit(1)
