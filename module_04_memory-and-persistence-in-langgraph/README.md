
# Memory & Persistence in LangGraph

Learn how LangGraph checkpointers save conversation state and restore it across interactions.

This module explores in-memory checkpointing, SQLite persistence, and PostgreSQL database storage.

## Topics Covered

- LangGraph checkpointers
- Conversation state and thread IDs
- In-memory checkpointing with MemorySaver
- Persistent storage using SQLite
- PostgreSQL checkpointing
- Conversation thread isolation

## Python Files

### Shared Agent

**File:** `memory_demo_agent.py`

Located in the module's main folder.

This shared file contains a simple rule-based conversation agent used by all three demonstrations.

It does not use an LLM or require an API key.

### Conversation Memory with MemorySaver

**Folder:** `conversation-memory-with-langgraph-checkpointers/`

**File:** `memory_saver.py`

Demonstrates:

- Conversation behavior without checkpointing
- In-memory checkpointing with MemorySaver
- Reusing conversation history with thread IDs
- Independent conversation threads
- Memory limitations after a restart

### SQLite Persistence

**Folder:** `persistent-conversation-memory-with-sqlite/`

**File:** `sqlite_persistence.py`

Demonstrates:

- Saving conversation state in SQLite
- Restoring previous conversations after restarting the program
- Using the same thread ID across sessions
- Resetting stored conversation history

The database is stored in `checkpoints.db`.

### PostgreSQL Persistence

**Folder:** `production-ready-persistence-with-postgresql/`

**File:** `postgres_persistence.py`

Demonstrates:

- PostgreSQL checkpointing with PostgresSaver
- Separate conversation threads
- Retrieving saved state through a new database connection
- Database-backed conversation persistence

## Running the Examples

All three scripts import `memory_demo_agent.py` from this module's main folder.

Navigate to the Module 4 folder first.

Add the current module directory to Python's import path.

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = (Get-Location).Path
```

**macOS / Linux:**

```bash
export PYTHONPATH="$(pwd)"
```

Then run the scripts from the module directory.

**MemorySaver:**

```bash
python conversation-memory-with-langgraph-checkpointers/memory_saver.py
```

**SQLite:**

```bash
python persistent-conversation-memory-with-sqlite/sqlite_persistence.py
```

To clear the saved SQLite history:

```bash
python persistent-conversation-memory-with-sqlite/sqlite_persistence.py --reset
```

No API key is required for these examples.

## PostgreSQL Setup

PostgreSQL is required only for the PostgresSaver demonstration.

Start Docker and create a PostgreSQL container:

```bash
docker run --name langgraph-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=langgraph_memory -p 5432:5432 -d postgres:16
```

If the container already exists, start it using:

```bash
docker start langgraph-db
```

Add the following to your repository's `.env` file:

```env
DATABASE_URL=postgresql://postgres:secret@localhost:5432/langgraph_memory
```

The password shown here is for the local demonstration.

Run:

```bash
python production-ready-persistence-with-postgresql/postgres_persistence.py
```

The program creates the checkpoint tables, tests separate conversation threads, and retrieves saved state through a new database connection.

## Installation

All Python dependencies are covered by the main repository README.

Docker and the PostgreSQL container are needed only for the PostgreSQL example.
