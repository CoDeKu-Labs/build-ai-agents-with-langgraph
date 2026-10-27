"""
Checkpointers and MemorySaver (in-memory persistence)

Install:  pip install langgraph
Run:      python conversation-memory-with-langgraph-checkpointers/memory_saver.py
Needs:    memory_demo_agent.py in the Module 4 root folder.
          The Module 4 root must be on PYTHONPATH.
          No API key required.

Four tests:
  0. No checkpointer: The agent forgets between calls.
  1. MemorySaver: Remembers conversations with the same thread_id.
  2. Different thread_id: Maintains separate conversations.
  3. Simulated restart: A new MemorySaver has no previous state.
"""

from memory_demo_agent import build_graph, say, saved_user_messages

# LangGraph 1.x calls this InMemorySaver. MemorySaver is the older name for the same thing.
try:
    from langgraph.checkpoint.memory import InMemorySaver as MemorySaver
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver


def step(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    input("Press Enter...")


if __name__ == "__main__":
    graph = build_graph()

    # ---- TEST 0: no checkpointer ----
    step("TEST 0: NO checkpointer (each call starts from scratch)")
    goldfish = graph.compile()
    say(goldfish, None, "I am planning a trip to Tokyo")
    say(goldfish, None, "My budget is $500")
    say(goldfish, None, "What did I tell you?")
    print("   -> Without a checkpointer, every invoke() starts with an empty state.")

    # ---- TEST 1: with MemorySaver ----
    step("TEST 1: the SAME agent, compiled with MemorySaver")
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)                 # THE ONLY CHANGE
    config = {"configurable": {"thread_id": "user-001"}}     # which conversation is this?

    say(app, config, "I am planning a trip to Tokyo")
    say(app, config, "My budget is $500")
    say(app, config, "What did I tell you?")
    print(f"\n   Saved for thread 'user-001': {saved_user_messages(app, config)}")

    # ---- TEST 2: a different thread_id ----
    step("TEST 2: a DIFFERENT thread_id is a separate conversation")
    other = {"configurable": {"thread_id": "user-002"}}
    say(app, other, "What did I tell you?")
    print("   -> user-002 has its own empty history. user-001's messages are not shared.")

    # ---- TEST 3: simulated restart ----
    step("TEST 3: 'server restart' (a brand new MemorySaver)")
    memory_after_restart = MemorySaver()                     # RAM is wiped: new, empty object
    app_after_restart = graph.compile(checkpointer=memory_after_restart)
    say(app_after_restart, config, "What did I tell you?")   # same thread_id as TEST 1
    print("   -> Same thread_id, but the memory lived in RAM and the RAM is gone.")
    print("   -> That is why MemorySaver is for testing. Next lesson: SQLite.")
