# Real-Time Streaming & Capstone AI Agent Project

Stream agent progress and LLM responses, then integrate course concepts into an Auto-HR Onboarding Agent.

## Topics

- Graph updates vs. streamed LLM messages
- Employee data extraction and validation
- Conditional routing, SQLite checkpointing, simulated approvals, and streaming

## Coding lessons

| Lesson | Code file(s) | What you build |
|---|---|---|
| [Real-Time Streaming in LangGraph](./real-time-streaming-in-langgraph/) | `streaming_demo.py` | Compare `ainvoke()` and `astream()` with graph updates and streamed LLM messages. |
| [Capstone Project — Auto-HR Onboarding Agent](./capstone-auto-hr-onboarding-agent/) | `auto_hr_onboarding.py` | Extract employee details, validate with Pydantic, apply simulated approval rules, persist chat state, and stream responses. |

## Working with the examples

Add each Python script to its matching lesson folder, install the packages used by that script, and run it from its lesson folder. Configure any required API keys or database connection details through environment variables.
