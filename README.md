
# Build AI Agents with LangGraph: Workflows, Memory & Streaming

Python code and practical examples for the second course in the Zero-to-Hero Agent Roadmap.

This repository covers LangGraph workflows, tool calling, conditional routing, parallel execution, Pydantic validation, asynchronous Python, conversation memory, database persistence, and real-time streaming.

## Course Modules

| Module | Topics |
|---|---|
| [Introduction to Agentic Frameworks & LangGraph](./module_01_introduction-to-agentic-frameworks-and-langgraph/) | Agent frameworks, production challenges, state, nodes, and edges |
| [Advanced LangGraph Workflows](./module_02_advanced-langgraph-workflows-conditional-routing-and-parallel-execution/) | Conditional routing, tool calling, and parallel execution |
| [Data Validation, Structured Outputs & Async AI Agents](./module_03_data-validation-structured-outputs-and-async-ai-agents/) | Pydantic, structured outputs, and async Python |
| [Memory & Persistence in LangGraph](./module_04_memory-and-persistence-in-langgraph/) | MemorySaver, SQLite, and PostgreSQL |
| [Real-Time Streaming & Capstone](./module_05_real-time-streaming-and-capstone-ai-agent-project/) | Streaming responses and Auto-HR Onboarding Agent |

Each module contains a README with its code examples and execution instructions.

## Requirements

- Python 3.11 or newer
- pip
- Groq API key for LLM-based examples
- Docker for the PostgreSQL demonstration

## Installation

Clone the repository and navigate to the project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows:**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

Install all required Python packages:

```bash
python -m pip install -U langgraph langchain-core langchain-groq groq pydantic python-dotenv requests langgraph-checkpoint-sqlite aiosqlite langgraph-checkpoint-postgres "psycopg[binary,pool]"
```

This installs the dependencies used throughout the course. You only need to install them once in your virtual environment.

## Environment Variables

Create a `.env` file in the repository root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

- `GROQ_API_KEY` is required for examples using Groq models.
- `GROQ_MODEL` is optional. You can change it to another supported Groq model.

The PostgreSQL lesson also requires a `DATABASE_URL`. Its module README includes the database setup instructions.

Do not commit your `.env` file to GitHub.

## Running the Examples

1. Open the module you want to study.
2. Read its `README.md`.
3. Navigate to the relevant lesson folder.
4. Run the Python script using `python filename.py`.

Some examples use simulated data and do not require an API key. Others connect to Groq or external APIs.

## Capstone Project

### Auto-HR Onboarding Agent

Build an AI agent that:

- Extracts employee information using an LLM
- Validates data with Pydantic
- Requests missing or invalid information
- Uses conditional routing and simulated approval rules
- Saves conversation state with SQLite
- Streams workflow progress and responses

The project combines the main concepts covered throughout the course.
