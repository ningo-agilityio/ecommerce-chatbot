import logging
from typing import Any, Optional
from langchain_core.memory import BaseMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain_community.chat_message_histories import ChatMessageHistory

class ConversationBufferWindowMemory(BaseChatMemory):
    k: int  # Number of recent message pairs to retain in memory
    buffer: Optional[ChatMessageHistory]  # Chat message history buffer
    def __init__(self, k: int = 5):
        buffer = ChatMessageHistory()
        super().__init__(k=k, buffer=buffer)
        self.k = k # Set buffer size
        self.buffer = buffer # Initialize an empty message history

    @property
    def memory_variables(self):
        # Define memory variables to store in the buffer
        return ["chat_history"]

    def load_memory_variables(self, inputs):
        # Provide the recent conversation history as a string of messages
        return {"chat_history": self._get_recent_conversations()}

    def save_context(self, inputs, outputs):
        # Append new interactions to the buffer
        self.buffer.add_user_message(inputs["input"])
        self.buffer.add_ai_message(outputs["output"])

        # Maintain only the last `k` messages
        if len(self.buffer.messages) > self.k * 2:  # Each interaction has a user and an AI message
            self.buffer.messages = self.buffer.messages[-self.k * 2:]

    def clear(self):
        # Clear the buffer
        self.buffer.clear()

    def _get_recent_conversations(self):
        # Convert buffer messages to text for memory variable use
        return "\n".join([msg.content for msg in self.buffer.messages])

# window_memory = ConversationBufferWindowMemory(k=5)
# window_memory.save_context({"input": "Hello, how are you?"}, {"output": "I'm good, thank you!"})
# window_memory.save_context({"input": "Tell me a joke."}, {"output": "Why did the chicken cross the road?"})

# # Load the conversation history to verify it
# history = window_memory.load_memory_variables({})
# print("Loaded conversation history:", history)