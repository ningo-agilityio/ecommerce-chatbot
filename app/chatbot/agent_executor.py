import logging
from dotenv import load_dotenv, find_dotenv
import os
import openai
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import HumanMessage

from app.chatbot.tools.tools import create_tools

class CustomConversationMemory:
    def __init__(self):
        self.conversation_history = []

    def load_memory_variables(self, inputs):
        # Return memory history as list of BaseMessage
        formatted_history = [
            {"role": "user", "content": message['output']} if isinstance(message, HumanMessage)
            else {"role": "assistant", "content": message['output']}
            for message in self.conversation_history
        ]
        return {"chat_history": formatted_history}

    def save_context(self, inputs, outputs):
        # Save user input and bot response
        bot_response = outputs.get("output", "")
        self.conversation_history.append(bot_response)

    def clear(self):
        # Clear the stored conversation history
        self.conversation_history = []

def _handle_error(error) -> str:
    print("_handle_error_agent")
    return str(error)[:50]

custom_memory = CustomConversationMemory()
tools = create_tools()
functions = [convert_to_openai_function(f) for f in tools]
model = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True).bind(functions=functions)

###### React agent
prompt_template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
prompt = ChatPromptTemplate.from_template(prompt_template)
react_agent = create_react_agent(
    llm=model,
    prompt=prompt,
    tools=tools
) 
agent_executor = AgentExecutor(
    agent=react_agent, 
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations = 5 # useful when agent is stuck in a loop
)

def run_with_memory(input_text, callback):
    # Load conversation history and include in input
    memory_variables = custom_memory.load_memory_variables({"input": input_text})
    full_input = {"input": input_text, **memory_variables}
    
    if callback is not None:
        chain_with_callbacks = agent_executor.with_config(callbacks=[callback])

        # Run the conversation
        response = chain_with_callbacks.invoke(full_input)
    else:
        response = agent_executor.invoke(full_input)
    # Save context (user input and AI response)
    custom_memory.save_context({"input": input_text}, {"output": response})

    return response

# Test conversation
# run_with_memory("How to order an online product?")
# run_with_memory("What is langchain?")
# run_with_memory("mini cake")
# run_with_memory("mousse")
# run_with_memory("order process")
