
# Data Validation, Structured Outputs & Async AI Agents

Learn how to validate AI agent inputs and outputs, generate structured LLM responses, and use asynchronous Python to improve execution efficiency.

## Topics Covered

- Pydantic models and field validation
- Custom validators and error handling
- Structured LLM outputs
- Schema validation vs. factual accuracy
- Async Python fundamentals
- Concurrent LangGraph execution

## Python Examples

### Pydantic Input Validation

**Folder:** `pydantic-for-ai-agents-input-validation/`

**File:** `pydantic_validation.py`

Learn to validate travel requests using Pydantic.

The example covers:

- `BaseModel` and `Field`
- Required and optional fields
- Custom validators
- Validation errors
- Type conversion
- Input validation before agent execution

**Run:**

```bash
cd pydantic-for-ai-agents-input-validation
python pydantic_validation.py
```

No API key is required.

### Structured LLM Outputs

**Folder:** `structured-llm-outputs-schemas-and-validation/`

**File:** `structured_output.py`

Generate and validate structured responses using Pydantic schemas and Groq.

The example demonstrates:

- Output schema definition
- `with_structured_output()`
- Schema validation
- Retry handling
- Comparing LLM-generated data against supplied source values

**Run:**

```bash
cd structured-llm-outputs-schemas-and-validation
python structured_output.py
```

The schema validation section works offline. The LLM section requires a Groq API key.

### Async Python & LangGraph

**Folder:** `async-python-building-non-blocking-ai-agents/`

**Files:**

- `async_basics.py`
- `async_langgraph.py`

**async_basics.py**

Compare synchronous and asynchronous execution using:

- `async def`
- `await`
- `asyncio.sleep()`
- `asyncio.gather()`
- Blocking vs. non-blocking operations

**async_langgraph.py**

Learn how to run multiple LangGraph requests concurrently using asynchronous nodes and `ainvoke()`.

**Run:**

```bash
cd async-python-building-non-blocking-ai-agents
python async_basics.py
python async_langgraph.py
```

Both examples use simulated API calls and do not require an API key.

## Installation

All dependencies are covered by the main repository README.

Python's `asyncio` library is included with Python and does not require separate installation.
