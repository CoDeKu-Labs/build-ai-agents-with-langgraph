"""
Parallel node execution (fan-out / fan-in)

Install:  pip install langgraph
Run:      python lesson_2_7_parallel_execution.py

This file builds the SAME three nodes twice:
  1. Sequential graph:  weather -> finance -> report
  2. Parallel graph:    weather + finance together -> report
and times both, so students SEE the difference.
"""

import operator
import time
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END


# Small stopwatch so timestamps are relative to the start of each run
clock = {"t0": 0.0}

def stamp() -> float:
    """Seconds since the current run started."""
    return time.perf_counter() - clock["t0"]

class TravelState(TypedDict):
    city: str
    budget_usd: float
    weather_data: str
    exchange_data: str
    final_report: str
    # BOTH parallel nodes add an entry here at the same time.
    # operator.add = the "guest book" rule: entries are appended, not overwritten.
    log: Annotated[list, operator.add]


# -----------------------------------------------------------
# NODES: time.sleep(3) pretends to be a slow API call.
# Each node writes a DIFFERENT field, so parallel nodes never clash.
# -----------------------------------------------------------
def weather_node(state: TravelState) -> dict:
    print(f"   [Weather] STARTED   t+{stamp():.1f}s")
    time.sleep(3)
    print(f"   [Weather] FINISHED  t+{stamp():.1f}s")
    return {"weather_data": f"{state['city']}: 18C, Rain 2mm", "log": ["weather done"]}


def finance_node(state: TravelState) -> dict:
    print(f"   [Finance] STARTED   t+{stamp():.1f}s")
    time.sleep(3)
    print(f"   [Finance] FINISHED  t+{stamp():.1f}s")
    return {
        "exchange_data": f"${state['budget_usd']} = {round(state['budget_usd'] * 149.5, 2)} JPY",
        "log": ["finance done"],
    }


def report_node(state: TravelState) -> dict:
    print(f"   [Report]  STARTED   t+{stamp():.1f}s  (both inputs are ready)")
    report = (
        "# Travel Advisory\n"
        f"**Weather:** {state['weather_data']}\n"
        f"**Budget:** {state['exchange_data']}"
    )
    return {"final_report": report}


# -----------------------------------------------------------
# GRAPH BUILDER: only the EDGES differ between the two versions
# -----------------------------------------------------------
def build_graph(parallel: bool):
    g = StateGraph(TravelState)
    g.add_node("weather", weather_node)
    g.add_node("finance", finance_node)
    g.add_node("report", report_node)

    if parallel:
        # FAN-OUT: two arrows leave START, so both nodes run together
        g.add_edge(START, "weather")
        g.add_edge(START, "finance")
        # FAN-IN: the list form means "wait for ALL of these, then run report"
        g.add_edge(["weather", "finance"], "report")
    else:
        # One long chain: each node waits for the previous one
        g.add_edge(START, "weather")
        g.add_edge("weather", "finance")
        g.add_edge("finance", "report")

    g.add_edge("report", END)
    return g.compile()


def run(label: str, app) -> float:
    print(f"\n=== {label} ===")
    clock["t0"] = time.perf_counter()
    result = app.invoke({"city": "Tokyo", "budget_usd": 500.0, "log": []})
    elapsed = time.perf_counter() - clock["t0"]
    print(f"   LOG  : {result['log']}")
    print(f"   TOTAL: {elapsed:.1f}s")
    return elapsed


if __name__ == "__main__":
    input("Press Enter to run BOTH versions (about 9 seconds total)...")

    sequential_time = run("SEQUENTIAL", build_graph(parallel=False))
    parallel_time = run("PARALLEL", build_graph(parallel=True))

    print("\n" + "=" * 50)
    print(f"Sequential : {sequential_time:.1f}s")
    print(f"Parallel   : {parallel_time:.1f}s")
    print(f"Speedup    : {sequential_time / parallel_time:.1f}x")
    print("=" * 50)
    print("Speedup = (sum of task times) / (longest single task).")
    print("It only works because weather and finance do NOT depend on each other.")
