import requests
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_weather_forecast(city: str, days: int = 3) -> str:
    """Fetches the live weather forecast for a specified city.
    
    Args:
        city: The name of the city (e.g., 'Colombo', 'Tokyo', 'London').
        days: Number of forecast days to retrieve (default is 3).
    """    
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_res = requests.get(geo_url).json()
    if not geo_res.get("results"):
        return f"Location {city} not found."
    lat = geo_res["results"][0]["latitude"]
    lon = geo_res["results"][0]["longitude"]
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,rain_sum&forecast_days={days}&timezone=auto"
    res = requests.get(weather_url).json()["daily"]
    return f"Forecast for {city}: Max Temps: {res['temperature_2m_max']}C, Rain Sum: {res['rain_sum']}mm."

def get_exchange_rate(amount: float, from_currency: str, to_currency: str) -> str:
    """Fetches the live exchange rate between two currencies (e.g. USD to JPY)."""
    url = f"https://open.er-api.com/v6/latest/{from_currency.upper()}"
    res = requests.get(url).json()
    
    if res.get("result") != "success":
        return f"Could not fetch exchange rate for {from_currency}."
        
    rates = res.get("rates", {})
    rate = rates.get(to_currency.upper())
    
    if not rate:
        return f"Currency code '{to_currency}' not found."
        
    total = round(amount * rate, 2)
    return f"{amount} {from_currency.upper()} = {total} {to_currency.upper()} (Live Rate: 1 {from_currency.upper()} = {rate} {to_currency.upper()})"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Fetches live weather forecast max temps and rain sum for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name e.g. Tokyo"},
                    "days": {"type": "integer", "description": "Number of forecast days"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Converts an amount from one currency to another using live exchange rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert e.g. 500"},
                    "from_currency": {"type": "string", "description": "Base currency code e.g. USD"},
                    "to_currency": {"type": "string", "description": "Target currency code e.g. JPY"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    }
]

messages = [{
    "role": "user", 
    "content": "I am planning a 3-day trip to Tokyo, Japan with a budget of $500 USD. Check the weather forecast for packing and convert my $500 USD budget to Japanese Yen (JPY) using today's live rate."
}]

print("[AGENT LOOP STARTED] LLM is fetching data using Tools...")

# Multi-turn Tool Loop
while True:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools_schema
    )

    msg = response.choices[0].message

    # 1. If tool_calls is None/empty -> LLM generated a plain text answer
    if not msg.tool_calls:
        print("The LLM replied directly with text (No tools requested).")

    # 2. If tool_calls contains data -> LLM requested one or more tool executions
    else:
        print(f"The LLM requested {len(msg.tool_calls)} Tool Call(s)!")
    
    messages.append(msg)

    if not msg.tool_calls:
        break

    for tool_call in msg.tool_calls:
        call_id = tool_call.id
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print("\n" + "="*50)
        print("[LLM DECISION DETECTED]")
        print(f"Tool Call ID : {call_id}")
        print(f"Function Name: {function_name}")
        print(f"Arguments    : {function_args}")
        print("="*50 + "\n")

        tool_output = ""
        if function_name == "get_weather_forecast":
            tool_output = get_weather_forecast(city=function_args.get("city"), days=function_args.get("days", 3))
        elif function_name == "get_exchange_rate":
            tool_output = get_exchange_rate(
                amount=float(function_args.get("amount", 1.0)), 
                from_currency=function_args.get("from_currency", "USD"), 
                to_currency=function_args.get("to_currency", "JPY")
            )
        else:
            tool_output = f"Error: Tool '{function_name}' not found."

        print(f"[TOOL OUTPUT]: {tool_output}")
        messages.append({
            "role": "tool", 
            "tool_call_id": tool_call.id, 
            "content": tool_output
            })

first_draft_report = messages[-1].content

print("\n" + "="*60)
print("[PAUSED] FIRST DRAFT COMPLETED!")
print("Here is the raw data compiled by the Agent BEFORE Reflection:")
print("-" * 40)
print(first_draft_report)
print("-" * 40)
print("="*60)

# The script stops here during your video so you can explain!
input("\nPress Enter to send this to the Senior Quality Auditor (Critic) for refinement...")

critic_prompt = f"""
You are a Senior Travel Quality Auditor. Review the following travel draft advisory:

--- DRAFT REPORT ---
{first_draft_report}

CRITIQUE CHECKLIST:
1. Does the packing list explicitly mention an umbrella or raincoat IF rain sum > 0mm?
2. Is the converted budget amount in JPY clearly stated with live rate?
3. Is it formatted in professional Markdown?

If anything is missing, refine it. Return ONLY the final polished Markdown Travel Advisory Report.
"""

reflection_response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": critic_prompt}]
)

final_polished_report = reflection_response.choices[0].message.content

print("\n================ FINAL POLISHED AGENT OUTPUT ================\n")
print(final_polished_report)



