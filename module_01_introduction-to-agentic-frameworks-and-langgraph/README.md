
# Introduction to Agentic Frameworks & LangGraph

This module introduces the challenges of building AI agents with pure Python, compares popular agentic frameworks, and explains the core concepts of LangGraph.

## Topics Covered

- Production challenges of pure Python agents
- CrewAI, AutoGen, and LangGraph
- Graph-based workflows
- State, nodes, and edges
- Graph compilation and execution

## Python Examples

### Weather & Travel Advisory Agent

**Folder:** `course_01_weather-travel-advisory-agent/`

**File:** `weather_travel_advisory_agent.py`

The final capstone from *Build Your First AI Agent: Tools, Loops & Self-Correction*.

This project uses pure Python, Groq, and external APIs to demonstrate tool calling and a reflection-based quality review.

It is used as a reference when exploring the challenges of basic Python agent implementations.

### LangGraph Fundamentals

**Folder:** `langgraph-fundamentals-state-nodes-and-edges/`

**File:** `langgraph_basics.py`

Build a simple LangGraph workflow using:

- `TypedDict` for state
- `StateGraph` for graph construction
- Weather and finance nodes
- Edges connecting nodes
- `invoke()` and `stream()` for execution

The weather and currency results in this example are simulated.

## Running the Examples

Install the dependencies using the main repository README.

For the original travel agent, follow the setup instructions inside its folder.

To run the LangGraph example:

```bash
cd langgraph-fundamentals-state-nodes-and-edges
python langgraph_basics.py
```

The LangGraph fundamentals example does not require an API key.
