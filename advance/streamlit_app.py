from chatbot.agent_executor import run_with_memory
import streamlit as st
import time

# import os
# from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

# Show title and description.
st.title("💬 Ecommerce Chatbot")
st.write(
    "This is a simple Ecommerce Chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
)

def get_response(user_query):
    return run_with_memory(user_query)

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am an e-commerce chatbot. How can I help you?"),
    ]

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        with st.spinner("Processing..."):
            # response = call_steamship(prompt, context)
            chain_response = get_response(user_query)
            # print(chain_response['output'])
            st.markdown(chain_response['output'])
            # response = st.write_stream(chain_response)
    st.session_state.chat_history.append(AIMessage(content=chain_response['output']))
    # st.session_state.chat_history.append(AIMessage(content=response))
