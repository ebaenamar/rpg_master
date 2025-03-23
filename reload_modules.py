import sys
import importlib

def reload_rag_modules():
    """Force reload of RAG-related modules to apply code changes"""
    # List of modules to reload
    modules_to_reload = [
        'rpg_game.rag.retriever',
        'rpg_game.orchestrator.game_orchestrator',
        'rag_helper'
    ]
    
    # Reload each module
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"Reloading module: {module_name}")
            importlib.reload(sys.modules[module_name])
        else:
            print(f"Module {module_name} not loaded yet")
    
    print("✅ All RAG modules reloaded successfully")
    print("Now you can run the game again!")

print("Add this code to your Jupyter notebook:")
print("\n" + "=" * 80 + "\n")
print("# Force reload of RAG modules to apply code changes")
print("from reload_modules import reload_rag_modules")
print("reload_rag_modules()")
print("\n" + "=" * 80 + "\n")
print("Run this cell before starting the game.")
