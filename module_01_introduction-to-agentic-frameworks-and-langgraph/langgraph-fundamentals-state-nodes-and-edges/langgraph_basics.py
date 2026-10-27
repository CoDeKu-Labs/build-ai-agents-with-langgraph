from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Course 1 functions (simulated)
def get_weather_forecast(city: str) -> str:
    return f"Weather forecast for {city}: 18C, Light Rain, 60% humidity"


def get_exchange_rate(amount: float, from_currency: str, to_currency: str) -> str:
    rate = 149.5
    return f"{amount} {from_currency} = {round(amount * rate, 2)} {to_currency} (rate: {rate})"

start_state = {"city": "Tokyo", "status": "order_received"}

# STEP 1: State = the "Order Book"
class TripState(TypedDict):
    city: str         # given at the start (the customer's order)
    weather: str      # filled by weather_node
    budget_jpy: str   # filled by finance_node
    status: str       # updated by every node


# STEP 2: Nodes = plain Python functions
def weather_node(state: TripState) -> dict:
    print(f"[Kitchen] Preparing weather for {state['city']}...")
    return {
        "weather": get_weather_forecast(state["city"]),
        "status": "weather_ready",
    }


def finance_node(state: TripState) -> dict:
    print("[Rider] Delivering budget conversion...")
    return {
        "budget_jpy": get_exchange_rate(500, "USD", "JPY"),
        "status": "all_done",
    }


# STEP 3: Graph = register nodes, then draw arrows
graph = StateGraph(TripState)

graph.add_node("weather", weather_node)
graph.add_node("finance", finance_node)

graph.add_edge(START, "weather")
graph.add_edge("weather", "finance")
graph.add_edge("finance", END)

# STEP 4: compile = check the wiring, get a runnable app
app = graph.compile()

# STEP 5: run it
result = app.invoke({"city": "Tokyo", "status": "order_received"})

for i, snapshot in enumerate(app.stream(start_state, stream_mode="values")):
    print(f"After step {i}: {snapshot}")

print(f"Weather: {result['weather']}")
print(f"Budget:  {result['budget_jpy']}")
print(f"Status:  {result['status']}")

