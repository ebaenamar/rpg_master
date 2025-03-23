import os
import sys
import importlib
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

def setup_for_jupyter():
    print("\n" + "=" * 60)
    print("Setting up RPG Game for Jupyter Notebook")
    print("=" * 60)
    
    # 1. Set up API key
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
        print("\nu274c No API key provided. Exiting.")
        return False
    
    # Set the API key in environment
    os.environ['AI21_API_KEY'] = api_key
    print("\nu2705 API key set in environment variables.")
    
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
            
            print("u2705 Updated API key in rpg_game_starter.py")
    except Exception as e:
        print(f"u26a0ufe0f Could not update rpg_game_starter.py: {e}")
    
    # 2. Test the API connection
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
            print("\nu2705 API test successful! Response:")
            print(f"AI: {response.choices[0].message.content}")
            print("\nYour API key is working correctly.")
        else:
            print("\nu274c API test failed: Received empty response")
            return False
            
    except Exception as e:
        print(f"\nu274c API test failed: {str(e)}")
        print("\nPlease check your API key and try again.")
        return False
    
    # 3. Force reload of modules
    print("\nReloading modules to apply code changes...")
    modules_to_reload = [
        'rpg_game.rag.retriever',
        'rpg_game.orchestrator.game_orchestrator',
        'rpg_game.agent.llm_agent',
        'rag_helper'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"Reloading module: {module_name}")
            importlib.reload(sys.modules[module_name])
        else:
            print(f"Module {module_name} not loaded yet")
    
    print("u2705 All modules reloaded successfully")
    print("\nSetup complete! You can now run the game.")
    return True

print("Add this code to your Jupyter notebook:")
print("\n" + "=" * 80 + "\n")
print("# Set up the RPG game for Jupyter")
print("from jupyter_setup import setup_for_jupyter")
print("success = setup_for_jupyter()")
print("# Only continue if setup was successful")
print("if success:")
print("    # Now you can run the game")
print("    main()")
print("\n" + "=" * 80 + "\n")
