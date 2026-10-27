# Advanced LangGraph Workflows — Conditional Routing & Parallel Execution

Build dynamic, tool-using LangGraph workflows and run independent graph nodes concurrently.

## Topics

- LLM tool binding and conditional edges
- Conversation state with message reducers
- Fan-out/fan-in workflows and safe state merging

## Coding lessons

| Lesson | Code file(s) | What you build |
|---|---|---|
| [Conditional Edges — Model-Driven Routing](./conditional-edges-model-driven-routing/) | `conditional_edges.py` | Build an agent with LLM, tool, and router nodes; select paths with conditional edges and test tool calls. |
| [Parallel Execution in LangGraph](./parallel-execution-in-langgraph/) | `parallel_execution.py` | Compare sequential and parallel graphs, merge independent results, and use reducers for shared fields. |

## Working with the examples

Add each Python script to its matching lesson folder, install the packages used by that script, and run it from its lesson folder. Configure any required API keys or database connection details through environment variables.
