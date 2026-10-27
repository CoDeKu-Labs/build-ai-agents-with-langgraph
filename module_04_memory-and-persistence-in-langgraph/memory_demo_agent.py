"""
Shared demo agent for Lessons 2.9, 2.10 and 2.11 (memory / checkpointers).

Why a shared file?
  All three lessons use the SAME agent. The only thing that changes from lesson
  to lesson is the checkpointer line: MemorySaver -> SqliteSaver -> PostgresSaver.

The "brain" is a tiny rule-based function instead of a real LLM, so you need
no API key and the result is always the same:
  - A STATEMENT  ('I am planning a trip to Tokyo')  -> the agent notes it.
  - A QUESTION   ('What did I tell you?')           -> the agent recalls the
                                                       earlier messages FROM THE STATE.
If the agent has no memory, a question gets 'You haven't told me anything yet.'
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]   # the conversation, new messages are appended


def chat_node(state: ChatState) -> dict:
    user_texts = [m.content for m in state["messages"] if m.type == "human"]
    latest, earlier = user_texts[-1], user_texts[:-1]

    if latest.strip().endswith("?"):
        if earlier:
            reply = "Earlier you told me: " + " | ".join(earlier)
        else:
            reply = "You haven't told me anything yet."
    else:
        reply = f"Noted. I now remember {len(user_texts)} message(s) from you."

    return {"messages": [AIMessage(content=reply)]}


def build_graph() -> StateGraph:
    """Returns the graph NOT yet compiled, so each lesson can choose its checkpointer."""
    graph = StateGraph(ChatState)
    graph.add_node("chat", chat_node)
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    return graph


def say(app, config, text: str, show_user: bool = True) -> str:
    """Send one user message, print the exchange, return the agent's reply."""
    result = app.invoke({"messages": [("user", text)]}, config=config)
    reply = result["messages"][-1].content
    if show_user:
        print(f"   You  : {text}")
    print(f"   Agent: {reply}")
    return reply


def saved_user_messages(app, config) -> list:
    """What the checkpointer has saved for this thread (only the user's messages)."""
    snapshot = app.get_state(config)
    messages = snapshot.values.get("messages", [])
    return [m.content for m in messages if m.type == "human"]
