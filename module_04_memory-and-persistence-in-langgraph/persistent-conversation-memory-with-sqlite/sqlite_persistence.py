"""
SqliteSaver (memory that survives a restart)

Install:  pip install langgraph langgraph-checkpoint-sqlite
Needs:    memory_demo_agent.py in the same folder. No API key.

HOW TO DEMO A REAL RESTART (two separate runs):
  Run 1:  python lesson_2_10_sqlite_persistence.py
          type:  I want to visit Tokyo for 3 days
          type:  My budget is $500 USD
          type:  quit                              <- the program ENDS
  Run 2:  python lesson_2_10_sqlite_persistence.py  <- a brand new process
          type:  What did I tell you?              <- it remembers

  Start over with:  python lesson_2_10_sqlite_persistence.py --reset

The memory lives in the file checkpoints.db (add it to .gitignore).
Note: this is the SYNC saver. For async apps (ainvoke) use AsyncSqliteSaver instead.
"""

import os
import sys

from langgraph.checkpoint.sqlite import SqliteSaver

from memory_demo_agent import build_graph, say, saved_user_messages

DB_FILE = "checkpoints.db"
THREAD_ID = "user-tokyo-trip"


def main() -> None:
    if "--reset" in sys.argv:
        for suffix in ("", "-wal", "-shm"):          # SQLite may create side files too
            if os.path.exists(DB_FILE + suffix):
                os.remove(DB_FILE + suffix)
        print("Deleted the old database. Starting fresh.")

    graph = build_graph()

    # The checkpointer is opened as a context manager: the file is closed on exit.
    with SqliteSaver.from_conn_string(DB_FILE) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)    # THE ONLY CHANGE vs Lesson 4.1
        config = {"configurable": {"thread_id": THREAD_ID}}

        earlier = saved_user_messages(app, config)
        if earlier:
            print(f"Found {len(earlier)} saved message(s) from a previous run:")
            for text in earlier:
                print(f"   - {text}")
        else:
            print("No saved conversation yet. This is a fresh start.")

        print("\nType a message. Type 'quit' to stop the program.")
        while True:
            text = input("\nYou: ").strip()
            if text.lower() in {"quit", "exit"}:
                break
            if text:
                say(app, config, text, show_user=False)

    print(f"\nProgram ended. Your conversation is saved in {DB_FILE}.")
    print("Run the script again: the agent will still remember.")


if __name__ == "__main__":
    main()
