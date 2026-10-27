
# Advanced LangGraph Workflows: Conditional Routing & Parallel Execution

Learn how to create dynamic AI workflows using conditional edges, tool calling, and parallel node execution in LangGraph.

## Topics Covered

- LLM-driven tool selection
- Conditional edges and routing functions
- Tool execution nodes
- Conversation state with `add_messages`
- Sequential vs. parallel execution
- Fan-out and fan-in workflows
- State reducers

## Python Examples

### Conditional Routing

**Folder:** `conditional-edges-model-driven-routing/`

**File:** `conditional_routing.py`

Build a tool-using LangGraph agent with:

- Weather and currency conversion tools
- Groq LLM integration
- `bind_tools()` for tool selection
- LLM, tool, and router nodes
- Conditional edges and execution loops
- Conversation state management

The tools use simulated weather and exchange-rate data.

**Run:**

```bash
cd conditional-edges-model-driven-routing
python conditional_routing.py
```

Requires `GROQ_API_KEY` in your `.env` file.

### Parallel Execution

**Folder:** `parallel-execution-in-langgraph/`

**File:** `parallel_execution.py`

Compare sequential and parallel execution using the same workflow nodes.

This example demonstrates:

- Sequential execution
- Parallel node execution
- Fan-out and fan-in
- State merging with reducers
- Execution time comparison

The program simulates slow API calls using `time.sleep()`.

**Run:**

```bash
cd parallel-execution-in-langgraph
python parallel_execution.py
```

No API key is required.

## Installation

All dependencies are covered by the main repository README.
