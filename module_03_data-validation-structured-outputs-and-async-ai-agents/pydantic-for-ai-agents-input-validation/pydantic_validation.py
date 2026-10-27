"""
Pydantic input validation

Install:  pip install pydantic
Run:      python pydantic_validation.py

No API key needed. This lesson validates the data that comes INTO your agent,
before it reaches the LLM or any tool.
"""

from typing import Optional

from pydantic import BaseModel, Field, ValidationError, field_validator


# -----------------------------------------------------------
# STEP 1: The model = the checklist the data must pass
# -----------------------------------------------------------
class TravelRequest(BaseModel):
    city: str = Field(..., min_length=2, description="Destination city name")
    trip_days: int = Field(..., ge=1, le=30, description="Number of travel days (1 to 30)")
    budget_usd: float = Field(..., gt=0, description="Budget in USD (must be above 0)")
    traveler_email: Optional[str] = Field(None, description="Optional contact email")

    # STEP 2: a custom rule for things Field() cannot express.
    # It runs AFTER the built-in checks above have passed.
    @field_validator("city")
    @classmethod
    def city_must_not_be_numeric(cls, value: str) -> str:
        if value.strip().isdigit():
            raise ValueError(f"City name cannot be a number: '{value}'")
        return value.strip().title()   # also cleans the value: 'tokyo' -> 'Tokyo'


# -----------------------------------------------------------
# STEP 3: turn Pydantic's error into short messages a user can read
# -----------------------------------------------------------
def friendly_errors(error: ValidationError) -> list[str]:
    messages = []
    for item in error.errors():
        field = ".".join(str(part) for part in item["loc"])
        messages.append(f"{field}: {item['msg']}")
    return messages


# -----------------------------------------------------------
# STEP 4: the function your agent calls BEFORE the LLM or any tool
# Returns (clean_request, []) or (None, [messages for the user])
# -----------------------------------------------------------
def validate_request(raw: dict) -> tuple[Optional[TravelRequest], list[str]]:
    try:
        return TravelRequest(**raw), []
    except ValidationError as error:
        return None, friendly_errors(error)


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


if __name__ == "__main__":
    # ---- TEST 1: valid input ----
    step("TEST 1: a valid request")
    request = TravelRequest(city="tokyo", trip_days=3, budget_usd=500.0, traveler_email="user@example.com")
    print(f"   City   : {request.city}        <- cleaned from 'tokyo'")
    print(f"   Days   : {request.trip_days}")
    print(f"   Budget : ${request.budget_usd}")
    print(f"   As dict: {request.model_dump()}   <- this is what you pass to the graph")

    # ---- TEST 2: negative days ----
    step("TEST 2: -5 days")
    try:
        TravelRequest(city="Tokyo", trip_days=-5, budget_usd=500.0)
    except ValidationError as error:
        print(f"   Caught: {type(error).__name__}")
        for message in friendly_errors(error):
            print(f"   - {message}")

    # ---- TEST 3: budget is not a number ----
    step("TEST 3: budget = 'abc'")
    try:
        TravelRequest(city="Tokyo", trip_days=3, budget_usd="abc")
    except ValidationError as error:
        for message in friendly_errors(error):
            print(f"   - {message}")

    # ---- TEST 4: custom validator ----
    step("TEST 4: city = '12345' (custom validator)")
    try:
        TravelRequest(city="12345", trip_days=3, budget_usd=500.0)
    except ValidationError as error:
        for message in friendly_errors(error):
            print(f"   - {message}")

    # ---- TEST 5: safe conversion ----
    step("TEST 5: strings that LOOK like numbers")
    converted = TravelRequest(city="Tokyo", trip_days="3", budget_usd="500")
    print(f"   trip_days '3'   -> {converted.trip_days!r}  (converted to int)")
    print(f"   budget '500'    -> {converted.budget_usd!r}  (converted to float)")
    try:
        TravelRequest(city="Tokyo", trip_days=3.5, budget_usd=500)
    except ValidationError as error:
        print(f"   trip_days 3.5   -> rejected: {friendly_errors(error)[0]}")
    print("   Rule: Pydantic converts when nothing is lost, and rejects when something would be.")

    # ---- TEST 6: use it as the gate in front of the agent ----
    step("TEST 6: the gate in front of the agent (all problems at once)")
    bad_input = {"city": "x", "trip_days": -5, "budget_usd": "abc"}
    clean, problems = validate_request(bad_input)
    if clean is None:
        print("   Request rejected. Tell the user:")
        for message in problems:
            print(f"   - {message}")
    good_input = {"city": "tokyo", "trip_days": 3, "budget_usd": 500}
    clean, problems = validate_request(good_input)
    if clean is not None:
        print(f"\n   Request accepted -> next step: app.invoke({clean.model_dump()})")
