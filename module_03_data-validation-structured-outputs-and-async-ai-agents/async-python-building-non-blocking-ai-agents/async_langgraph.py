"""
async LangGraph, serving several users at once

Install:  pip install langgraph
Run:      python async_langgraph.py

Two rules for async LangGraph:
  1. Write nodes as `async def` and use `await` for anything that waits.
     (For a real LLM that means `await llm.ainvoke(...)`.)
  2. Run the graph with `await app.ainvoke(...)` instead of `app.invoke(...)`.
     Graphs with async nodes are meant to be run with `ainvoke`.
"""

import asyncio
import os
import time
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

DELAY = float(os.getenv("DEMO_DELAY", "1"))   # seconds per fake API call


class TripState(TypedDict):
    city: str
    weather_data: str
    exchange_data: str


async def weather_node(state: TripState) -> dict:
    await asyncio.sleep(DELAY)             # pretend: await weather_api(...)
    return {"weather_data": f"{state['city']}: 18C, Rain 2mm"}


async def finance_node(state: TripState) -> dict:
    await asyncio.sleep(DELAY)             # pretend: await exchange_api(...)
    return {"exchange_data": "500 USD = 74750.0 JPY"}


graph = StateGraph(TripState)
graph.add_node("weather", weather_node)
graph.add_node("finance", finance_node)
graph.add_edge(START, "weather")
graph.add_edge("weather", "finance")
graph.add_edge("finance", END)
app = graph.compile()

USERS = ["Tokyo", "Colombo", "Paris"]


async def one_user_at_a_time() -> float:
    start = time.perf_counter()
    for city in USERS:
        await app.ainvoke({"city": city})       # wait for each user to finish first
    return time.perf_counter() - start


async def all_users_together() -> float:
    start = time.perf_counter()
    await asyncio.gather(*(app.ainvoke({"city": city}) for city in USERS))
    return time.perf_counter() - start


if __name__ == "__main__":
    input("Press Enter to serve 3 users ONE AT A TIME...")
    slow = asyncio.run(one_user_at_a_time())
    print(f"   TOTAL: {slow:.1f}s   (3 users x 2 steps x {DELAY:g}s)")

    input("\nPress Enter to serve the same 3 users TOGETHER...")
    fast = asyncio.run(all_users_together())
    print(f"   TOTAL: {fast:.1f}s   (about as long as ONE user)")

    print(f"\nSpeedup: {slow / fast:.1f}x")
    print("Each user's own steps are still in order (weather, then finance).")
    print("What runs at the same time is DIFFERENT users.")
