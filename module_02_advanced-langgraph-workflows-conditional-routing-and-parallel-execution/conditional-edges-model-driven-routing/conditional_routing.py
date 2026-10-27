"""
Conditional Edges — the LLM decides, your router routes

Install:  pip install langgraph langchain-groq langchain-core python-dotenv
Needs:    GROQ_API_KEY in your .env
Optional: GROQ_MODEL in .env (Groq retires models often; default below)

The loop:   START -> llm --(wants a tool?)--> tools -> llm -> ... -> END
                           \\--(final answer)--> END

Who does what:
  - The LLM only ASKS for a tool (it never runs one).
  - tool_node RUNS the tool and hands back the result.
  - should_use_tool() is plain Python that reads the LLM's last message
    and picks the next node.
"""

import os
from typing import TypedDict, Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

SYSTEM_PROMPT = (
    "You are a helpful travel assistant. Use the tools when you need weather "
    "or currency data. If the user just chats, answer directly without tools."
)


# -----------------------------------------------------------
# TOOLS (the Course 1 functions, simulated).
# The docstring is what the LLM reads to decide when to use the tool.
# -----------------------------------------------------------
DEMO_WEATHER = {  # simulated data so the answers look realistic
    "tokyo": "18C, Light Rain",
    "colombo": "30C, Partly Cloudy",
}


@tool
def get_weather_forecast(city: str) -> str:
    """Get the weather forecast for a city."""
    print(f"      [TOOL RAN] get_weather_forecast('{city}')")
    forecast = DEMO_WEATHER.get(city.strip().lower(), "24C, Clear")
    return f"Weather forecast for {city}: {forecast}"


@tool
def get_exchange_rate(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount of money from one currency to another."""
    print(f"      [TOOL RAN] get_exchange_rate({amount}, {from_currency}, {to_currency})")
    rate = 149.5  # fixed demo rate
    return f"{amount} {from_currency} = {round(amount * rate, 2)} {to_currency} (rate: {rate})"


# Build a lookup dictionary:
# tool name (string) -> actual LangChain tool object
#
# Conceptually:
# {
#     "get_weather_forecast": <StructuredTool object>,
#     "get_exchange_rate":    <StructuredTool object>,
# }

tools = [get_weather_forecast, get_exchange_rate]
TOOLS_BY_NAME = {t.name: t for t in tools}

# Give the LLM the "menu" of tools it is allowed to ask for
llm = ChatGroq(model=MODEL, temperature=0)
llm_with_tools = llm.bind_tools(tools)


# -----------------------------------------------------------
# STEP 1: State.
# In Lesson 2.3 every box simply got OVERWRITTEN by the newest value.
# A conversation needs the opposite: the `messages` box is a GUEST BOOK
# where every new entry is ADDED to the end. That rule is a "reducer".
# add_messages is the "append" reducer built for chat messages.
# -----------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# -----------------------------------------------------------
# STEP 2: LLM node = the "brain". It asks; it does not run tools.
# The system prompt is added at call time and is NOT stored in state.
# -----------------------------------------------------------
def llm_node(state: AgentState) -> dict:
    print("[LLM Node] Thinking...")
    response = llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}


# -----------------------------------------------------------
# STEP 3: Tool node = the "hands". Runs whatever the brain asked for.
# tool_call_id links each result back to its request (like a receipt number).
# -----------------------------------------------------------
def tool_node(state: AgentState) -> dict:
    print("[Tool Node] Running requested tools...")
    last_message = state["messages"][-1]
    results = []

    for call in last_message.tool_calls:
        name, args = call["name"], call["args"]
        print(f"   -> {name}({args})")
        try:
            output = TOOLS_BY_NAME[name].invoke(args)
        except Exception as e:  # send errors back to the LLM as text
            output = f"Tool error: {e}"
        results.append(ToolMessage(content=str(output), tool_call_id=call["id"], name=name))

    return {"messages": results}


# -----------------------------------------------------------
# STEP 4: THE ROUTER = the traffic light. Plain Python, easy to test.
# Replaces Course 1's:  if not msg.tool_calls: break
# -----------------------------------------------------------
def should_use_tool(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        print("[Router] LLM asked for a tool -> go to tools")
        return "tools"

    print("[Router] LLM gave a final answer -> go to END")
    return END


# -----------------------------------------------------------
# STEP 5: Build the graph
# -----------------------------------------------------------
graph = StateGraph(AgentState)
graph.add_node("llm", llm_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "llm")

# THE KEY LINE: after "llm", ask the router where to go next
graph.add_conditional_edges("llm", should_use_tool, {"tools": "tools", END: END})

# The loop-back arrow: tool results go back to the brain
graph.add_edge("tools", "llm")

app = graph.compile()


# -----------------------------------------------------------
# Helper: run one question and print the whole conversation path
# -----------------------------------------------------------
def ask(question: str) -> None:
    print(f"\nUSER: {question}")
    # recursion_limit = safety net: stops a runaway tool loop
    result = app.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 10},
    )

    print("\n--- Conversation path ---")
    for m in result["messages"]:
        kind = type(m).__name__
        calls = getattr(m, "tool_calls", None)
        if calls:
            print(f"  {kind}: asked for {[c['name'] for c in calls]}")
        else:
            print(f"  {kind}: {str(m.content)[:100]}")

    print(f"\nFINAL ANSWER: {result['messages'][-1].content}")


if __name__ == "__main__":
    print(f"Using model: {MODEL}")

    input("\nTEST 1 (no tool needed). Press Enter...")
    ask("Hello, how are you?")

    input("\nTEST 2 (one tool). Press Enter...")
    ask("What is the weather in Colombo?")

    input("\nTEST 3 (two tools). Press Enter...")
    ask("Plan a Tokyo trip: weather forecast and convert 500 USD to JPY.")
