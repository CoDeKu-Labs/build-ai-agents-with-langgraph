# Data Validation, Structured Outputs & Async AI Agents

Validate agent inputs and outputs, and use asynchronous Python to handle I/O-bound work efficiently.

## Topics

- Pydantic models, constraints, and custom validators
- Structured LLM responses and source-data cross-checking
- `async`, `await`, `asyncio.gather()`, and LangGraph `ainvoke()`

## Coding lessons

| Lesson | Code file(s) | What you build |
|---|---|---|
| [Pydantic for AI Agents — Input Validation](./pydantic-for-ai-agents-input-validation/) | `pydantic_validation.py` | Define travel-request schemas, validate incoming data, and return clear validation errors. |
| [Structured LLM Outputs — Schemas & Validation](./structured-llm-outputs-schemas-and-validation/) | `structured_output.py` | Apply output schemas, handle validation failures, and compare structured output against supplied facts. |
| [Async Python — Building Non-Blocking AI Agents](./async-python-building-non-blocking-ai-agents/) | `async_basics.py`, `async_langgraph.py` | Contrast blocking and non-blocking I/O, then run multiple LangGraph conversations concurrently. |

## Working with the examples

Add each Python script to its matching lesson folder, install the packages used by that script, and run it from its lesson folder. Configure any required API keys or database connection details through environment variables.
