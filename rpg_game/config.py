import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI21 API Configuration
AI21_API_KEY = os.getenv('AI21_API_KEY')
DEFAULT_MODEL = "jamba-mini-1.6-2025-03"  # Use the latest model available

# Game Configuration
GAME_TITLE = "Medieval Chronicles: The Fallen Knight"
DEBUG_MODE = False

# RAG Configuration
VECTOR_DB_PATH = "./data/vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformers model
RAG_TOP_K = 3  # Number of relevant passages to retrieve

# Scoring Configuration
INITIAL_ALIGNMENT = {
    "law_chaos": 0,    # -100 (Chaotic) to 100 (Lawful)
    "good_evil": 0,   # -100 (Evil) to 100 (Good)
    "trust": 50       # 0 (No trust) to 100 (Complete trust)
}

# LLM Agent Configuration
DEFAULT_AGENT = {
    "name": "Ser Elyen",
    "class": "Knight",
    "alignment": "Neutral Good",
    "backstory": "A fallen knight seeking redemption after failing to protect his liege lord."
}
