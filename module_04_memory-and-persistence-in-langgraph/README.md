# Memory & Persistence in LangGraph

Use checkpointers to preserve and resume conversation state, first in RAM and then in SQLite and PostgreSQL.

## Topics

- MemorySaver and conversation thread IDs
- SQLite persistence across restarts
- PostgreSQL checkpointing and thread isolation

## Coding lessons

| Lesson | Code file(s) | What you build |
|---|---|---|
| [Conversation Memory with LangGraph Checkpointers](./conversation-memory-with-langgraph-checkpointers/) | `memory_saver_demo.py` | Compare runs with and without MemorySaver, demonstrate thread isolation, and explain restart limitations. |
| [Persistent Conversation Memory with SQLite](./persistent-conversation-memory-with-sqlite/) | `sqlite_persistence.py` | Store checkpoints in a local SQLite database and recover history after restarting the program. |
| [Production-Ready Persistence with PostgreSQL](./production-ready-persistence-with-postgresql/) | `postgres_persistence.py` | Connect LangGraph to PostgreSQL, compare conversation threads, and restore history through a fresh connection. |

## Shared code

`memory_demo_agent.py` contains the simple rule-based conversation agent reused across the three persistence demonstrations. Keep this helper at the module root and update imports in the lesson scripts accordingly.

## Working with the examples

Add each Python script to its matching lesson folder, install the packages used by that script, and run it from its lesson folder. Configure any required API keys or database connection details through environment variables.
