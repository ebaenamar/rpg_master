import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional

# Import the helper modules
try:
    from rag_helper import setup_rag_system, RAGHelper
    from agent_helper import setup_llm_agent, LLMAgentHelper
    _helpers_imported = True
except ImportError:
    _helpers_imported = False

def setup_notebook_environment():
    """Set up the environment for the RPG game notebook"""
    print("Setting up the RPG game environment...")
    
    # Check if we're running in a notebook
    try:
        from IPython import get_ipython
        if get_ipython() is None:
            print("This script should be run from within a Jupyter notebook.")
            return False
    except ImportError:
        print("IPython is not installed. This script should be run from within a Jupyter notebook.")
        return False
    
    # Install required packages if not already installed
    required_packages = [
        'ai21', 'faiss-cpu', 'langchain', 'langchain-community', 
        'sentence-transformers', 'chromadb', 'python-dotenv', 'pydantic'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"❌ Missing package: {package}. Installing...")
            try:
                # Use IPython's built-in shell command
                get_ipython().run_line_magic('pip', f'install {package}')
                print(f"✅ Installed {package}")
            except Exception as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    print("✅ All required packages are installed.")
    
    # Set up API key
    api_key = os.environ.get('AI21_API_KEY')
    if not api_key:
        print("⚠️ AI21_API_KEY not found in environment variables.")
        api_key = input("Please enter your AI21 API key: ")
        os.environ['AI21_API_KEY'] = api_key
        print("✅ API key set successfully.")
    else:
        print("✅ AI21_API_KEY found in environment variables.")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/vector_db", exist_ok=True)
    print("✅ Data directories created.")
    
    # Check if we need to create sample data files
    create_sample_data_if_needed()
    
    # Load game data
    game_data = {}
    try:
        with open("data/game_data.json", "r") as f:
            game_data = json.load(f)
        print(f"✅ Game data loaded: {len(game_data.get('scenes', []))} scenes found.")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"❌ Error loading game data: {e}")
        return False
    
    # Load historical data
    historical_data = []
    try:
        with open("data/historical_data.json", "r") as f:
            historical_data = json.load(f)
        print(f"✅ Historical data loaded: {len(historical_data)} entries found.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error loading historical data: {e}")
        return False
    
    # Initialize RAG system
    if _helpers_imported:
        print("\nInitializing RAG system...")
        rag_helper = setup_rag_system("data/historical_data.json")
        if rag_helper is None:
            print("❌ Failed to initialize RAG system")
            return False
        
        # Test LLM agent connection
        print("\nTesting LLM agent connection...")
        agent_helper = setup_llm_agent(api_key)
        if agent_helper is None:
            print("❌ Failed to initialize LLM agent")
            return False
    else:
        print("⚠️ Helper modules not imported. Some functionality may be limited.")
    
    print("\n✅ Environment setup complete. You can now run the game!")
    return True

def create_sample_data_if_needed():
    """Create sample data files if they don't exist"""
    # Create sample game data if it doesn't exist
    if not os.path.exists("data/game_data.json"):
        print("⚠️ Game data file not found. Creating sample game data...")
        sample_game_data = {
            "game_title": "Medieval Chronicles: The Fallen Knight",
            "scenes": [
                {
                    "id": "intro",
                    "title": "The Road to Canterbury",
                    "description": "You find yourself on the dusty road to Canterbury. The year is 1215, and England is in turmoil. King John's tyranny has pushed the barons to rebellion, and rumors of a great charter being drafted have reached even the most remote villages. As you travel, you notice a weathered knight resting by the roadside, his armor dented but well-maintained.",
                    "next_scenes": ["canterbury_gates", "forest_detour", "village_rest"],
                    "historical_context_keywords": ["magna carta", "king john", "canterbury"]
                },
                {
                    "id": "canterbury_gates",
                    "title": "The Gates of Canterbury",
                    "description": "The imposing gates of Canterbury stand before you, guarded by the sheriff's men who eye travelers with suspicion. The cathedral spires rise majestically beyond the walls, a beacon of faith in troubled times. Ser Elyen, the knight you met on the road, stands beside you, his hand resting casually on his sword hilt.",
                    "next_scenes": ["cathedral_sanctuary", "tavern_information", "market_supplies"],
                    "historical_context_keywords": ["canterbury cathedral", "thomas becket", "medieval city guards"]
                }
            ],
            "player": {
                "alignment": {
                    "law_chaos": 50,  # 0 = Chaotic, 100 = Lawful
                    "good_evil": 50    # 0 = Evil, 100 = Good
                },
                "relationships": {
                    "ser_elyen": {
                        "trust": 50,    # 0 = Distrusts, 100 = Trusts completely
                        "description": "Cautious acquaintance"
                    }
                }
            }
        }
        with open("data/game_data.json", "w") as f:
            json.dump(sample_game_data, f, indent=2)
        print("✅ Sample game data created.")
    
    # Create sample historical data if it doesn't exist
    if not os.path.exists("data/historical_data.json"):
        print("⚠️ Historical data file not found. Creating sample historical data...")
        sample_historical_data = [
            {
                "title": "Magna Carta",
                "text": "The Magna Carta was a charter of liberties agreed to by King John of England in 1215. It was the first document forced onto an English King by his subjects in an attempt to limit his powers by law and protect their rights. The charter was a major step in the historical process that led to the rule of constitutional law in the English-speaking world.",
                "year": "1215",
                "category": "political",
                "source": "historical_records"
            },
            {
                "title": "Thomas Becket",
                "text": "Thomas Becket was Archbishop of Canterbury from 1162 until his murder in 1170. He engaged in conflict with King Henry II over the rights and privileges of the Church. The King had Becket murdered by four knights in Canterbury Cathedral. Becket was canonized shortly after his death and became one of the most important saints in England, with Canterbury Cathedral becoming a major pilgrimage site.",
                "year": "1170",
                "category": "religious",
                "source": "historical_records"
            },
            {
                "title": "King John of England",
                "text": "King John ruled England from 1199 to 1216. His reign was marked by disputes with the Church, leading to his excommunication, and conflicts with his barons, resulting in the Magna Carta. John was considered a cruel and unsuccessful monarch. He lost the Duchy of Normandy and much of his other French lands to King Philip II of France, leading to the nickname 'Lackland'.",
                "year": "1199-1216",
                "category": "political",
                "source": "historical_records"
            },
            {
                "title": "Medieval Canterbury",
                "text": "Canterbury was one of England's most important cities during the medieval period, primarily due to its cathedral being the seat of the Archbishop of Canterbury, the leader of the Church in England. After Thomas Becket's martyrdom in 1170, Canterbury became one of Europe's most important pilgrimage sites, as immortalized in Chaucer's 'Canterbury Tales'.",
                "year": "1170-1400",
                "category": "cultural",
                "source": "historical_records"
            }
        ]
        with open("data/historical_data.json", "w") as f:
            json.dump(sample_historical_data, f, indent=2)
        print("✅ Sample historical data created.")

def fine_tune_prompts():
    """Fine-tune the LLM prompts for better character interaction"""
    # These are improved prompts for the LLM character agent
    prompts = {
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
    
    print("✅ LLM prompts have been fine-tuned for better character interaction.")
    return prompts

# This function can be called from the notebook to get the fine-tuned prompts
def get_fine_tuned_prompts():
    return fine_tune_prompts()

# This function can be used to get a fully initialized game environment
def get_game_environment(api_key: Optional[str] = None):
    """Get a fully initialized game environment with RAG and LLM agent"""
    if not _helpers_imported:
        print("❌ Helper modules not imported. Cannot initialize game environment.")
        return None, None
    
    # Initialize RAG system
    rag_helper = setup_rag_system("data/historical_data.json")
    if rag_helper is None:
        print("❌ Failed to initialize RAG system")
        return None, None
    
    # Initialize LLM agent
    agent_helper = setup_llm_agent(api_key)
    if agent_helper is None:
        print("❌ Failed to initialize LLM agent")
        return None, None
    
    return rag_helper, agent_helper
