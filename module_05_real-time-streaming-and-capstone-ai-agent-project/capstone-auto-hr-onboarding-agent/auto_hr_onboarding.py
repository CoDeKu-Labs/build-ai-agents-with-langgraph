"""
CAPSTONE - Auto-HR Onboarding Agent

Install:
  pip install -U langgraph langgraph-checkpoint-sqlite aiosqlite langchain-groq pydantic python-dotenv

Needs:
  GROQ_API_KEY in your .env
Optional:
  GROQ_MODEL in your .env

Run:
  python auto_hr_onboarding.py
  python auto_hr_onboarding.py --demo
  python auto_hr_onboarding.py --demo-reject
  python auto_hr_onboarding.py --reset

Graph:
  START -> extract -> validate
                       | problems -> reply -> END
                       | valid -> approval
                                  | rejected -> reply -> END
                                  | approved -> onboard -> reply -> END

Important:
  This lesson does NOT use LangGraph interrupt() yet.
  If information is missing, the current graph run ends after replying.
  The user's next message starts a new run with the SAME thread_id.
  The checkpointer restores the saved conversation state.
"""

import asyncio
import os
import re
import sys
import time
from datetime import date, timedelta
from typing import Annotated, Literal, Optional, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, ValidationError, field_validator

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
API_KEY = os.getenv("GROQ_API_KEY")
DB_FILE = "hr_onboarding.db"

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found. Add GROQ_API_KEY=your_key to your .env file."
    )

llm = ChatGroq(model=MODEL, api_key=API_KEY, temperature=0)


# ===========================================================
# STEP 1: PYDANTIC - define what a valid employee record looks like
# ===========================================================
DEPARTMENTS = {
    "engineering": "Engineering",
    "marketing": "Marketing",
    "hr": "HR",
    "finance": "Finance",
}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmployeeDetails(BaseModel):
    full_name: str = Field(min_length=3)
    email: str
    department: Literal["Engineering", "Marketing", "HR", "Finance"]
    start_date: date

    @field_validator("full_name")
    @classmethod
    def tidy_name(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("not a valid email address")
        return value

    @field_validator("department", mode="before")
    @classmethod
    def normalize_department(cls, value):
        if isinstance(value, str):
            return DEPARTMENTS.get(value.strip().lower(), value)
        return value


FIELD_HINTS = {
    "full_name": "your full legal name (at least 3 characters)",
    "email": "a valid email address, like name@company.com",
    "department": "one of: Engineering, Marketing, HR, Finance",
    "start_date": "your start date in YYYY-MM-DD format",
}


def explain(error: ValidationError) -> list[str]:
    """Convert technical Pydantic errors into short messages for the user."""
    problems = []

    for item in error.errors():
        field = str(item["loc"][0]) if item["loc"] else "details"
        kind = "missing" if item["type"] == "missing" else "invalid"
        hint = FIELD_HINTS.get(field, item["msg"])
        problems.append(f"{field} ({kind}): {hint}")

    return problems


# ===========================================================
# STEP 2: STRUCTURED EXTRACTION - LLM extracts only stated facts
# ===========================================================
class ExtractedDetails(BaseModel):
    full_name: Optional[str] = Field(
        None, description="Full name, only if the user explicitly stated it"
    )
    email: Optional[str] = Field(
        None, description="Email, only if the user explicitly stated it"
    )
    department: Optional[str] = Field(
        None, description="Department, only if the user explicitly stated it"
    )
    start_date: Optional[str] = Field(
        None, description="Start date exactly as the user stated it"
    )


EXTRACT_PROMPT = (
    "Extract ONLY details explicitly stated by the new hire: "
    "full_name, email, department, start_date. "
    "If a detail has not been stated, return null. "
    "Never guess or invent a value."
)

REPLY_PROMPT = (
    "You are a friendly HR onboarding assistant. "
    "Be brief: at most 3 sentences. "
    "Use only the verified facts and problems you are given. "
    "Do not invent details."
)

# Function calling works across Groq models that support tools and keeps extraction structured.
extractor = llm.with_structured_output(
    ExtractedDetails,
    method="function_calling",
)


# ===========================================================
# STEP 3: STATE - shared data used by the graph
# ===========================================================
class HRState(TypedDict):
    messages: Annotated[list, add_messages]
    extracted: dict
    employee: dict
    problems: list
    stage: str


# ===========================================================
# STEP 4: NODES
# ===========================================================
async def extract_node(state: HRState) -> dict:
    """Read the user's messages and extract the details they have provided so far."""

    # Only use HumanMessage objects for extraction.
    # This prevents the model from treating the agent's own words as user-provided facts.
    user_messages = [
        message for message in state["messages"] if isinstance(message, HumanMessage)
    ]

    try:
        result = await extractor.ainvoke(
            [SystemMessage(content=EXTRACT_PROMPT), *user_messages]
        )
        extracted = result.model_dump() if result else {}
    except Exception as error:
        print(f"   (extraction problem: {type(error).__name__})")
        extracted = {}

    # Reset stage because this is a fresh user turn.
    return {"extracted": extracted, "stage": ""}


def validate_node(state: HRState) -> dict:
    """Validate the extracted data using normal Python + Pydantic."""
    provided = {
        key: value
        for key, value in state["extracted"].items()
        if value is not None and value != ""
    }

    try:
        employee = EmployeeDetails(**provided)
    except ValidationError as error:
        return {
            "employee": {},
            "problems": explain(error),
            "stage": "needs_info",
        }

    return {
        "employee": employee.model_dump(mode="json"),
        "problems": [],
        "stage": "validated",
    }


def approval_node(state: HRState) -> dict:
    """Simulated HR approval rule. Real human interrupt comes in a later lesson."""
    start = date.fromisoformat(state["employee"]["start_date"])

    if start < date.today():
        reason = (
            f"the start date {start} is in the past; "
            "please provide today or a future date"
        )
        return {"problems": [reason], "stage": "rejected"}

    return {"stage": "approved"}


def onboard_node(state: HRState) -> dict:
    """Simulate the final onboarding action."""
    return {"stage": "onboarded"}


async def reply_node(state: HRState) -> dict:
    """Turn verified state into a short, friendly response."""
    stage = state["stage"]
    problems = state["problems"]
    employee = state["employee"]

    if stage == "needs_info":
        task = (
            "Politely ask the new hire only for these missing or invalid items: "
            f"{problems}"
        )
    elif stage == "rejected":
        task = (
            "Explain politely that HR cannot approve the details yet because: "
            f"{problems[0]}. Ask for a corrected start date."
        )
    else:  # onboarded
        task = (
            f"Welcome {employee['full_name']}, who is joining "
            f"{employee['department']} on {employee['start_date']}. "
            f"Say that next steps will be emailed to {employee['email']}."
        )

    system = REPLY_PROMPT + "\n\nCURRENT TASK: " + task
    response = await llm.ainvoke(
        [SystemMessage(content=system), *state["messages"]]
    )

    return {"messages": [response]}


# ===========================================================
# STEP 5: ROUTERS
# ===========================================================
def after_validate(state: HRState) -> Literal["approval", "reply"]:
    return "reply" if state["problems"] else "approval"


def after_approval(state: HRState) -> Literal["onboard", "reply"]:
    return "onboard" if state["stage"] == "approved" else "reply"


# ===========================================================
# STEP 6: BUILD THE GRAPH
# ===========================================================
def build_graph() -> StateGraph:
    graph = StateGraph(HRState)

    graph.add_node("extract", extract_node)
    graph.add_node("validate", validate_node)
    graph.add_node("approval", approval_node)
    graph.add_node("onboard", onboard_node)
    graph.add_node("reply", reply_node)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "validate")

    graph.add_conditional_edges(
        "validate",
        after_validate,
        {"approval": "approval", "reply": "reply"},
    )

    graph.add_conditional_edges(
        "approval",
        after_approval,
        {"onboard": "onboard", "reply": "reply"},
    )

    graph.add_edge("onboard", "reply")
    graph.add_edge("reply", END)

    return graph


# ===========================================================
# STEP 7: STREAM ONE CHAT TURN
# ===========================================================
def describe(node: str, update: dict) -> str:
    """Create a short progress line for node-level streaming."""
    if not update:
        return ""

    if node == "extract":
        found = [key for key, value in update["extracted"].items() if value]
        return "found: " + (", ".join(found) if found else "nothing yet")

    if node == "validate":
        return (
            "all details valid"
            if not update["problems"]
            else f"{len(update['problems'])} problem(s) found"
        )

    if node == "approval":
        return "HR approved" if update["stage"] == "approved" else "HR rejected"

    if node == "onboard":
        return "onboarding records created (simulated)"

    return ""


async def chat_turn(app, config: dict, user_text: str) -> None:
    """Run one user message through the graph and stream progress + reply tokens."""
    print(f"\nYou  : {user_text}")
    reply_started = False

    async for mode, data in app.astream(
        {"messages": [("user", user_text)]},
        config=config,
        stream_mode=["updates", "messages"],
    ):
        if mode == "updates":
            for node, update in data.items():
                note = describe(node, update)
                if note:
                    print(f"   [{node}] {note}")

        elif mode == "messages":
            chunk, metadata = data

            # Only show tokens produced by the reply node.
            is_reply = metadata.get("langgraph_node") == "reply"
            has_text = isinstance(chunk.content, str) and bool(chunk.content)

            if is_reply and has_text:
                if not reply_started:
                    print("Agent: ", end="", flush=True)
                    reply_started = True

                print(chunk.content, end="", flush=True)

    print()


# ===========================================================
# STEP 8: DEMO INPUTS + SAVED STATE
# ===========================================================
def demo_messages(kind: str) -> list[str]:
    future = (date.today() + timedelta(days=30)).isoformat()

    if kind == "reject":
        return [
            "Hi, I'm Nimali Silva, nimali@company.com, joining Finance. "
            "My start date is 2020-01-15."
        ]

    return [
        "Hi! I'm Kamal Perera and I'm joining the Engineering department.",
        "My email is kamal@@company",
        f"Sorry, typo. It's kamal@company.com, and I start on {future}.",
    ]


async def show_saved_state(app, config: dict) -> None:
    snapshot = await app.aget_state(config)
    values = snapshot.values

    print("\n--- Saved in the database for this thread ---")
    print(f"   messages : {len(values.get('messages', []))}")
    print(f"   stage    : {values.get('stage')}")
    print(f"   employee : {values.get('employee')}")


# ===========================================================
# STEP 9: MAIN PROGRAM
# ===========================================================
async def main() -> None:
    args = sys.argv[1:]

    if "--reset" in args:
        for suffix in ("", "-wal", "-shm"):
            path = DB_FILE + suffix
            if os.path.exists(path):
                os.remove(path)
        print("Deleted the saved conversations.")

    if "--demo-reject" in args:
        demo = "reject"
    elif "--demo" in args:
        demo = "happy"
    else:
        demo = None

    # Demo runs use a fresh thread. Interactive mode keeps one stable thread to show memory.
    thread_id = f"new-hire-{int(time.time())}" if demo else "new-hire-001"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Model: {MODEL} | thread_id: {thread_id}")

    # Because the graph runs asynchronously, use the async SQLite checkpointer.
    async with AsyncSqliteSaver.from_conn_string(DB_FILE) as checkpointer:
        app = build_graph().compile(checkpointer=checkpointer)

        if demo:
            for text in demo_messages(demo):
                await asyncio.to_thread(input, "\nPress Enter for the next message...")
                await chat_turn(app, config, text)
        else:
            saved = await app.aget_state(config)
            count = len(saved.values.get("messages", []))

            if count:
                print(f"Resuming a saved conversation ({count} messages).")
            else:
                print("New conversation.")

            print("Type your messages as the new hire. Type 'quit' to stop.")

            while True:
                text = (await asyncio.to_thread(input, "\n> ")).strip()

                if text.lower() in {"quit", "exit"}:
                    break

                if text:
                    await chat_turn(app, config, text)

        await show_saved_state(app, config)


if __name__ == "__main__":
    asyncio.run(main())
