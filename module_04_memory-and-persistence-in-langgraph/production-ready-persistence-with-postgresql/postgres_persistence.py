"""
PostgresSaver (production persistence) and thread isolation

Install:  pip install langgraph langgraph-checkpoint-postgres "psycopg[binary,pool]" python-dotenv
Needs:    memory_demo_agent.py in the same folder. No API key.

Start a local database (Docker must be running). POSTGRES_DB creates the database
named in DATABASE_URL, otherwise the connection fails:

  docker run --name langgraph-db -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=langgraph_memory -p 5432:5432 -d postgres:16

Then put this in your .env  (demo password only, never use it in production):

  DATABASE_URL=postgresql://postgres:secret@localhost:5432/langgraph_memory
"""

import os
import time
from urllib.parse import urlparse

from langgraph.checkpoint.postgres import PostgresSaver

from memory_demo_agent import build_graph, say, saved_user_messages

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def safe_url(url: str) -> str:
    """Never print the password."""
    parts = urlparse(url)
    host = f"{parts.hostname}:{parts.port}" if parts.port else parts.hostname
    return f"{parts.scheme}://{host}{parts.path}  (credentials hidden)"


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


def main() -> None:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL is not set. See the top of this file for the docker command and the .env line.")
        return

    print(f"Connecting to: {safe_url(db_url)}")
    graph = build_graph()

    # Fresh thread ids on every run, so old demo data never confuses the counts.
    run_id = int(time.time())
    thread_a = {"configurable": {"thread_id": f"user-a-tokyo-{run_id}"}}
    thread_b = {"configurable": {"thread_id": f"user-b-colombo-{run_id}"}}

    # ---------------------------------------------------------------
    # PART 1: two users, one agent, one database
    # ---------------------------------------------------------------
    with PostgresSaver.from_conn_string(db_url) as checkpointer:
        checkpointer.setup()                       # creates the checkpoint tables (safe to repeat)
        app = graph.compile(checkpointer=checkpointer)   # THE ONLY CHANGE

        step("PART 1: user A and user B talk to the same agent")
        print("User A (thread A):")
        say(app, thread_a, "I am planning a trip to Tokyo")
        say(app, thread_a, "My budget is $500")
        print("\nUser B (thread B):")
        say(app, thread_b, "What is the weather in Colombo")
        say(app, thread_b, "I need an umbrella")

        step("PART 2: each user asks what they said. Is each history isolated?")
        print("User A:")
        say(app, thread_a, "What did I tell you about my trip?")
        print("\nUser B:")
        say(app, thread_b, "What did I ask you earlier?")

        a_texts = saved_user_messages(app, thread_a)
        b_texts = saved_user_messages(app, thread_b)
        shared = set(a_texts) & set(b_texts)
        print(f"\n   Saved for A: {len(a_texts)} message(s)")
        print(f"   Saved for B: {len(b_texts)} message(s)")
        print(f"   Messages found in BOTH threads: {len(shared)}")
        print("   ISOLATION CHECK:", "PASSED" if not shared else "FAILED")
        print("   (This demo runs the users one after another. In production, many")
        print("    requests reach the database at once, and that is what Postgres is built for.)")

    # ---------------------------------------------------------------
    # PART 3: a NEW connection, like a different server instance
    # ---------------------------------------------------------------
    step("PART 3: a brand new connection (think: another server) reads user A's history")
    with PostgresSaver.from_conn_string(db_url) as checkpointer_2:
        app_2 = graph.compile(checkpointer=checkpointer_2)
        say(app_2, thread_a, "What did I tell you?")
    print("   -> The history was in the database, not in any one server's memory.")


if __name__ == "__main__":
    main()
