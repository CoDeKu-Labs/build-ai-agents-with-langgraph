"""
Structured output (and what it does NOT check)

Install:  pip install pydantic langchain-groq python-dotenv
Needs:    GROQ_API_KEY in your .env for PART B (PART A works offline)
Optional: GROQ_MODEL in .env (Groq retires models often; default below)

KEY IDEA
  A schema checks the FORMAT of the LLM's answer: field types, ranges, allowed values.
  It does NOT check that the answer is TRUE.
  To get true answers: give the LLM real data (grounding), then cross-check against it.
"""

import os
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


# -----------------------------------------------------------
# STEP 1: the OUTPUT schema = the form the LLM must fill in
# -----------------------------------------------------------
class WeatherReport(BaseModel):
    city: str = Field(description="The city name")
    temperature_celsius: float = Field(description="Temperature in Celsius")
    condition: Literal["Sunny", "Rainy", "Cloudy"] = Field(description="Weather condition")
    rain_probability_percent: int = Field(ge=0, le=100, description="Rain chance, 0 to 100")
    packing_suggestion: str = Field(description="One-line packing advice")


def show_errors(error: ValidationError) -> None:
    for item in error.errors():
        field = ".".join(str(part) for part in item["loc"])
        print(f"      - {field}: {item['msg']}")


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


# -----------------------------------------------------------
# PART A (offline): what the schema accepts and rejects
# -----------------------------------------------------------
def part_a_schema_checks() -> None:
    good = {
        "city": "Colombo", "temperature_celsius": 30.0, "condition": "Cloudy",
        "rain_probability_percent": 40, "packing_suggestion": "Light clothes and an umbrella",
    }
    bad_cases = {
        "rain = 150 (out of range)": {**good, "rain_probability_percent": 150},
        "condition = 'Foggy' (not allowed)": {**good, "condition": "Foggy"},
        "temperature = 'hot' (not a number)": {**good, "temperature_celsius": "hot"},
        "packing_suggestion missing": {k: v for k, v in good.items() if k != "packing_suggestion"},
    }

    report = WeatherReport(**good)
    print(f"   GOOD data  -> {type(report).__name__}: {report.city}, {report.temperature_celsius}C, {report.condition}")

    for label, data in bad_cases.items():
        print(f"\n   BAD data: {label}")
        try:
            WeatherReport(**data)
        except ValidationError as error:
            show_errors(error)


# -----------------------------------------------------------
# PART B (needs a Groq key): structured output from a real LLM
# -----------------------------------------------------------
def ask_structured(structured_llm, prompt: str, attempts: int = 2) -> WeatherReport:
    """LangChain does NOT retry for you. If the output does not fit the schema
    you get an exception, so we add a small retry loop ourselves."""
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            result = structured_llm.invoke(prompt)
            if result is None:
                raise ValueError("The model returned no structured output")
            return result
        except Exception as error:   # schema mismatch, parsing error, ...
            last_error = error
            print(f"      attempt {attempt} failed: {type(error).__name__}")
    raise last_error


def check_against_source(report: WeatherReport, facts: dict) -> list[str]:
    """The cross-check: does the LLM's answer match the real data we gave it?"""
    problems = []
    for key, expected in facts.items():
        actual = getattr(report, key)
        if actual != expected:
            problems.append(f"{key}: source says {expected!r}, LLM said {actual!r}")
    return problems


def part_b_real_llm() -> None:
    if not os.getenv("GROQ_API_KEY"):
        print("   GROQ_API_KEY not found in your environment. Skipping PART B.")
        return

    from langchain_groq import ChatGroq   # imported here so PART A runs without it

    llm = ChatGroq(model=MODEL, temperature=0)

    # THE KEY LINE: the schema is attached to the model.
    # LangChain uses the model's tool-calling / JSON feature behind the scenes
    # and parses the reply into a WeatherReport object.
    structured_llm = llm.with_structured_output(WeatherReport)

    # ---- B1: no data given ----
    step("B1: ask for tomorrow's weather WITHOUT giving any data")
    report = ask_structured(structured_llm, "Give me a weather report for Colombo, Sri Lanka for tomorrow.")
    print(f"   Type   : {type(report).__name__}")
    print(f"   City   : {report.city}")
    print(f"   Temp   : {report.temperature_celsius}C")
    print(f"   Rain   : {report.rain_probability_percent}%")
    print(f"   Packing: {report.packing_suggestion}")
    print("\n   The FORMAT is perfect. But no tool or data was given,")
    print("   so where did these numbers come from? The LLM guessed them.")

    # ---- B2: real data given ----
    step("B2: give the LLM REAL data, then cross-check its answer")
    facts = {  # in a real agent this comes from your weather tool
        "city": "Colombo",
        "temperature_celsius": 30.0,
        "condition": "Cloudy",
        "rain_probability_percent": 40,
    }
    prompt = (
        f"Use ONLY this data from our weather tool: {facts}. "
        "Fill in the weather report and write a one-line packing suggestion."
    )
    report = ask_structured(structured_llm, prompt)
    print(f"   Packing: {report.packing_suggestion}")

    problems = check_against_source(report, facts)
    if problems:
        print("   CROSS-CHECK FAILED:")
        for problem in problems:
            print(f"   - {problem}")
    else:
        print("   CROSS-CHECK PASSED: every number matches the source data.")


if __name__ == "__main__":
    step("PART A: what the schema accepts and rejects (offline)")
    part_a_schema_checks()

    step("PART B: structured output from a real LLM")
    part_b_real_llm()
