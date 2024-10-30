import logging
import uuid
from langchain_core.messages import HumanMessage, BaseMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

# workflow = StateGraph(state_schema=MessagesState)

class CustomerConversationWindowMemory:
    memory: MemorySaver

    def __init__(self):
        self.memory = MemorySaver()

    def state_modifier(state) -> list[BaseMessage]:
        logging.info("state_modifier")
        logging.info(state)
        """Given the agent state, return a list of messages for the chat model."""
        # We're using the message processor defined above.
        return trim_messages(
            state["messages"],
            token_counter=len,  # <-- len will simply count the number of messages rather than tokens
            max_tokens=5,  # <-- allow up to 5 messages.
            strategy="last",
            # Most chat models expect that chat history starts with either:
            # (1) a HumanMessage or
            # (2) a SystemMessage followed by a HumanMessage
            # start_on="human" makes sure we produce a valid chat history
            start_on="human",
            # Usually, we want to keep the SystemMessage
            # if it's present in the original history.
            # The SystemMessage has special instructions for the model.
            include_system=True,
            allow_partial=False,
        )

# Define the two nodes we will cycle between
# workflow.add_edge(START, "model")
# workflow.add_node("model", call_model)

# Adding memory is straight forward in langgraph!


# app = workflow.compile(
#     checkpointer=memory
# )

# # The thread id is a unique key that identifies
# # this particular conversation.
# # We'll just generate a random uuid here.
# thread_id = uuid.uuid4()
# config = {"configurable": {"thread_id": thread_id}}

# input_message = HumanMessage(content="hi! I'm bob")
# for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
#     event["messages"][-1].pretty_print()

# # Here, let's confirm that the AI remembers our name!
# config = {"configurable": {"thread_id": thread_id}}
# input_message = HumanMessage(content="what was my name?")
# for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
#     event["messages"][-1].pretty_print()