# Build AI Agents with LangGraph: Workflows, Memory & Streaming

This repository organizes the Python examples from the Zero-to-Hero Agent Roadmap LangGraph course. The folders follow the module topics; each coding lesson has its own directory. Conceptual lessons without Python code are covered within the relevant module README rather than given empty lesson directories.

## Modules

| Module | Focus |
|---|---|
| [Introduction to Agentic Frameworks & LangGraph](./introduction-to-agentic-frameworks-and-langgraph/) | Understand the limitations of simple Python agents, evaluate agentic frameworks, and learn the fundamental building blocks of LangGraph. |
| [Advanced LangGraph Workflows — Conditional Routing & Parallel Execution](./advanced-langgraph-workflows-conditional-routing-and-parallel-execution/) | Build dynamic, tool-using LangGraph workflows and run independent graph nodes concurrently. |
| [Data Validation, Structured Outputs & Async AI Agents](./data-validation-structured-outputs-and-async-ai-agents/) | Validate agent inputs and outputs, and use asynchronous Python to handle I/O-bound work efficiently. |
| [Memory & Persistence in LangGraph](./memory-and-persistence-in-langgraph/) | Use checkpointers to preserve and resume conversation state, first in RAM and then in SQLite and PostgreSQL. |
| [Real-Time Streaming & Capstone AI Agent Project](./real-time-streaming-and-capstone-ai-agent-project/) | Stream agent progress and LLM responses, then integrate course concepts into an Auto-HR Onboarding Agent. |

## Repository layout

Each module contains a README with its concepts and corresponding coding lessons. Lesson directories are named for their topics rather than numbered. A few lessons contain multiple Python scripts, while the memory module includes one helper shared across its examples.

## Getting started

1. Open the README inside the module you are studying.
2. Add the Python source files listed there to the matching lesson folders.
3. Install the packages used in the example, set up any required environment variables, and run the script.

The source scripts are not included in this folder template; add the original lesson code before running the examples. Remove each `.gitkeep` file after adding its Python script.

## Capstone

**Auto-HR Onboarding Agent** — A LangGraph workflow that extracts employee information, validates inputs with Pydantic, requests missing details, uses simulated approval rules, stores conversation state using SQLite, and streams responses.
