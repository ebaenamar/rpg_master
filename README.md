# Medieval Chronicles: The Fallen Knight

A text-based, historically grounded roleplaying game (RPG) powered by AI21's language models. This agentic system features dynamic storytelling, historical context via RAG (Retrieval-Augmented Generation), moral decision-making, and an interactive LLM-driven NPC companion. Now available as a Jupyter Notebook for an enhanced interactive experience!

## 🔮 Game Concept

This RPG is inspired by systems like Kingdom Come: Deliverance and Dungeons & Dragons. The player engages in an interactive story where they control one human character, while a second companion character (Ser Elyen) is controlled by a Language Model (LLM). The game is structured as a sequence of scenes, each offering four dynamically generated choices that lead to different moral, narrative, and relationship consequences.

The world is grounded in real medieval history, retrieved via a Retrieval-Augmented Generation (RAG) system that provides historical context to the LLM agent and game logic.

## 🧱 System Architecture

The system is composed of five main components:

1. **Game Orchestrator**: The central controller that manages game flow, scene logic, and player choices.
2. **RAG Retriever**: Provides real-world historical context to ground the experience in accurate medieval facts.
3. **Scoring Engine**: Tracks player alignment, relationship with the LLM agent, and other stats.
4. **Behavior Controller**: Manages the LLM agent's personality and responses based on game state.
5. **LLM Character Agent**: The AI-controlled companion character that responds to player actions.

### Technical Implementation Details

#### RAG System Implementation

The Retrieval-Augmented Generation (RAG) system is implemented using the following technologies:

- **ChromaDB**: Used as the vector database for storing and retrieving documents
- **LangChain**: Provides the framework for connecting the RAG components
- **Sentence Transformers**: Creates embeddings of the text data

The RAG flow works as follows:

1. Historical data is embedded and stored in ChromaDB during initialization
2. Each game scene includes a `rag_context_query` and `rag_filter_tags`
3. When a scene is loaded, the query is sent to the RAG retriever along with filter tags
4. The retriever searches for similar documents in ChromaDB using the `similarity_search` method
5. Retrieved documents are formatted and returned as historical context
6. This historical context is passed to the LLM agent to generate informed responses

The system supports filtering by tags using the `$in` operator, allowing for more targeted retrieval based on the current scene's themes.

#### LLM Character Agent

The AI-controlled character (Ser Elyen) is powered by AI21's language models, specifically using the `jamba-mini-1.6-2025-03` model. The agent:

1. Receives context about the current scene, historical information from RAG, and player actions
2. Maintains a conversation history to provide continuity in responses
3. Generates contextually appropriate responses based on the player's choices and the game state
4. Adapts its personality based on the player's alignment and relationship scores

#### Game Flow

The game orchestrator manages the flow of the game by:

1. Loading scene data from `game_data.json`
2. Presenting the player with scene descriptions and action choices
3. Processing player actions and calculating score changes
4. Retrieving historical context via the RAG system
5. Passing all necessary context to the LLM agent for response generation
6. Determining the next scene based on the player's choice

## 📋 Requirements

- Python 3.8+
- AI21 API key
- Jupyter Notebook (for notebook version)

## 🛠️ Installation

### Standard Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your AI21 API key:

```
AI21_API_KEY=your_api_key_here
```

### Jupyter Notebook Setup

1. Create a Python virtual environment:

```bash
python -m venv rpg_venv
source rpg_venv/bin/activate  # On Windows: rpg_venv\Scripts\activate
```

2. Install the required packages:

```bash
pip install -r requirements.txt
pip install jupyter ipywidgets
```

3. Register the virtual environment as a Jupyter kernel:

```bash
pip install ipykernel
python -m ipykernel install --user --name=rpg_venv --display-name="RPG Game Environment"
```

4. Set your AI21 API key in the environment:

```bash
export AI21_API_KEY=your_api_key_here  # On Windows: set AI21_API_KEY=your_api_key_here
```

5. Run the Jupyter Notebook:

```bash
jupyter notebook rpg_game_demo.ipynb
```

## 🎮 Usage

### Standard Version

Run the game with:

```bash
python main.py
```

Follow the prompts to enter your character name and make choices throughout the story.

### Jupyter Notebook Version

1. Open the `rpg_game_demo.ipynb` notebook in Jupyter
2. Make sure to select the "RPG Game Environment" kernel
3. Run the cells in order to set up the environment and start the game
4. Interact with the game using the buttons generated in the notebook

## 🧠 Game Features

- **Dynamic Storytelling**: Each scene offers four choices with different consequences
- **Historical Accuracy**: RAG system provides real medieval context
- **Character Development**: Your alignment evolves based on choices
- **Relationship System**: Build trust with your AI companion
- **Moral Consequences**: Actions affect your Law-Chaos and Good-Evil alignment
- **Interactive Notebook**: Play the game in an interactive Jupyter environment (notebook version)
- **Debugging Tools**: Built-in debug output to monitor RAG retrieval and LLM responses

## 📚 Game Data

The game data is stored in JSON format in the `data` directory:

- `game_data.json`: Contains scene descriptions, actions, and consequences
- `historical_data.json`: Historical facts for the RAG system
- `save_game.json`: Created when you save your game progress

## 🔧 Customization

You can customize the game by:

1. Editing `game_data.json` to add new scenes and storylines
2. Adding more historical facts to `historical_data.json`
3. Modifying the scoring effects in `game_data.json` to change how actions impact alignment
4. Fine-tuning the LLM prompts in `notebook_helper.py` or `agent_helper.py`
5. Adding debug print statements to `retriever.py` to see RAG in action
6. Extending the game with more scenes to create a longer adventure

## 🛠 API Integration & Troubleshooting

This game relies on the AI21 API for generating character responses. Here are some important details:

### API Key Setup

- The game requires a valid AI21 API key to function properly
- The key can be set in several ways:
  1. As an environment variable: `export AI21_API_KEY=your_key_here`
  2. In the `.env` file in the project root
  3. Directly in the `rpg_game_starter.py` file (for testing only)
  4. Using the `jupyter_setup.py` script for Jupyter notebook users

### Model Information

- The game uses AI21's `jamba-mini-1.6-2025-03` model
- This model name is configured in `rpg_game/config.py`
- If AI21 releases new models, update the `DEFAULT_MODEL` variable in the config file

### Common Issues

1. **401 Unauthorized Error**: This indicates an issue with your API key. Make sure it's correctly set and valid.
2. **422 Unprocessable Entity**: This may occur if using an outdated model name. Check the model name in the config file.
3. **RAG Not Working**: Verify that the ChromaDB is properly initialized and that the query and filter tags are correctly formatted.

### Deployment

The code is designed to be deployed on Vercel, so no local npm install is needed. After making working changes, commit and push with:

```bash
git add . && git commit -m "chore: deploy memories" && git push
```

## 📝 License

This project is open source and available for educational and personal use.

## 🙏 Acknowledgments

- AI21 Labs for their powerful language models
- Historical sources that inspired the medieval setting
