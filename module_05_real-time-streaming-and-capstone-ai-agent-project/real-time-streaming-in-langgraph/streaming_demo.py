"""
Streaming (see the answer while it is being written)

Install:  pip install -U langgraph langchain-groq python-dotenv
Needs:    GROQ_API_KEY in your .env
Optional: GROQ_MODEL in .env
Note:     Python 3.11+ is recommended for async examples.

The SAME graph is run three ways:
  1. ainvoke()                         -> final result only
  2. astream(stream_mode="updates")   -> one update when each node finishes
  3. astream(stream_mode="messages")  -> LLM tokens as they are generated
"""

import asyncio
import os
import time
from typing import Annotated, TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found. Add GROQ_API_KEY=your_key to your .env file."
    )

PROMPT = (
    "Write a warm welcome message of about 120 words for a new employee "
    "joining the engineering team."
)

# LangGraph can stream model output while the graph is running.
llm = ChatGroq(model=MODEL, api_key=API_KEY, temperature=0)


class StreamState(TypedDict):
    messages: Annotated[list, add_messages]
    word_count: int


async def write_node(state: StreamState) -> dict:
    """Node 1: ask the LLM to write the welcome message."""
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


def count_node(state: StreamState) -> dict:
    """Node 2: count words using normal Python."""
    text = str(state["messages"][-1].content)
    return {"word_count": len(text.split())}


# Build one small graph: START -> write -> count_words -> END
graph = StateGraph(StreamState)
graph.add_node("write", write_node)
graph.add_node("count_words", count_node)
graph.add_edge(START, "write")
graph.add_edge("write", "count_words")
graph.add_edge("count_words", END)
app = graph.compile()

INPUTS = {"messages": [("user", PROMPT)]}


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


async def demo_ainvoke() -> None:
    """Demo 1: wait for the entire graph to finish."""
    start = time.perf_counter()
    print("   Waiting for the complete result...")

    result = await app.ainvoke(INPUTS)

    elapsed = time.perf_counter() - start
    print(f"\n   Everything arrived at once after {elapsed:.1f}s:\n")
    print(result["messages"][-1].content)
    print(f"\n   [{result['word_count']} words]")


async def demo_updates() -> None:
    """Demo 2: receive one update each time a node finishes."""
    start = time.perf_counter()

    async for update in app.astream(INPUTS, stream_mode="updates"):
        for node_name, node_output in update.items():
            elapsed = time.perf_counter() - start
            returned_fields = list(node_output.keys())
            print(
                f"   [{elapsed:4.1f}s] node '{node_name}' finished "
                f"-> returned {returned_fields}"
            )

    print("\n   We can see graph progress, but not the answer token by token.")


async def demo_tokens() -> None:
    """Demo 3: receive LLM text token by token."""
    start = time.perf_counter()
    first_token_time = None

    print()

    async for chunk, metadata in app.astream(INPUTS, stream_mode="messages"):
        # This graph has one LLM node. Filtering by node name makes the idea explicit.
        is_writer = metadata.get("langgraph_node") == "write"

        if is_writer and isinstance(chunk.content, str) and chunk.content:
            if first_token_time is None:
                first_token_time = time.perf_counter() - start

            print(chunk.content, end="", flush=True)

    total = time.perf_counter() - start

    print()
    if first_token_time is not None:
        print(
            f"\n   First token after {first_token_time:.1f}s; "
            f"full response finished after {total:.1f}s."
        )
    else:
        print(f"\n   Stream finished after {total:.1f}s, but no text chunks were received.")


async def main() -> None:
    print(f"Using model: {MODEL}")

    step("DEMO 1: ainvoke() -> wait for everything")
    await demo_ainvoke()

    step("DEMO 2: stream_mode='updates' -> node-by-node progress")
    await demo_updates()

    step("DEMO 3: stream_mode='messages' -> token streaming")
    await demo_tokens()


if __name__ == "__main__":
    asyncio.run(main())
