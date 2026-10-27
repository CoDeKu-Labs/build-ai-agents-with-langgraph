
# Real-Time Streaming & Capstone AI Agent Project

Learn how to stream LangGraph execution progress and LLM responses, then combine the course concepts into a complete Auto-HR Onboarding Agent.

## Topics Covered

- LangGraph streaming
- `ainvoke()` vs. `astream()`
- Workflow updates and LLM token streaming
- Structured data extraction
- Pydantic validation
- Conditional routing
- SQLite conversation persistence

## Python Examples

### Real-Time Streaming in LangGraph

**Folder:** `real-time-streaming-in-langgraph/`

**File:** `streaming_demo.py`

Compare three execution methods:

- `ainvoke()` — returns the completed result
- `astream(stream_mode="updates")` — streams graph node updates
- `astream(stream_mode="messages")` — streams LLM-generated text

The example uses Groq to generate an employee welcome message and demonstrates how streaming changes the user experience.

**Run:**

```bash
cd real-time-streaming-in-langgraph
python streaming_demo.py
```

Requires `GROQ_API_KEY` in your `.env` file.

### Capstone: Auto-HR Onboarding Agent

**Folder:** `capstone-auto-hr-onboarding-agent/`

**File:** `auto_hr_onboarding.py`

Build an employee onboarding agent using LangGraph.

**Features:**

- Extract employee details from conversations
- Validate information using Pydantic
- Identify missing or invalid details
- Ask users for corrections
- Apply simulated HR approval rules
- Route requests using conditional edges
- Store conversation state using AsyncSqliteSaver
- Stream execution updates and LLM responses

**Workflow:**

```text
START
  |
Extract Details
  |
Validate
  |
  |-- Invalid/Missing --> Reply --> END
  |
  |-- Valid --> Approval Check
                  |
                  |-- Rejected --> Reply --> END
                  |
                  |-- Approved --> Onboard --> Reply --> END
```

## Running the Capstone

Navigate to the capstone folder:

```bash
cd capstone-auto-hr-onboarding-agent
```

**Interactive mode:**

```bash
python auto_hr_onboarding.py
```

Chat with the agent as a new employee.

**Successful onboarding demo:**

```bash
python auto_hr_onboarding.py --demo
```

Demonstrates missing information, invalid email correction, successful validation, and onboarding.

**Rejected onboarding demo:**

```bash
python auto_hr_onboarding.py --demo-reject
```

Demonstrates a valid employee record rejected by the simulated approval rule because its start date is in the past.

**Reset conversation memory:**

```bash
python auto_hr_onboarding.py --reset
```

Deletes the saved SQLite conversation data before starting the application.

## Configuration

The streaming example and capstone require a Groq API key.

Configure it in the repository's `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

The capstone automatically uses a local SQLite database named `hr_onboarding.db`.

No PostgreSQL setup is needed for the capstone.

## Notes

- HR approval is simulated using Python business rules.
- Actual human-in-the-loop approval with LangGraph `interrupt()` is not implemented in this project.
- The onboarding actions are simulated rather than connected to a real HR system.

## Installation

All dependencies are covered by the main repository README.
