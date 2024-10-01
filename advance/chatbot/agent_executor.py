import os
from google_shopping_service import GoogleShoppingService
import openai

from dotenv import load_dotenv, find_dotenv
from tools import create_tools, search_online_products, search_wikipedia
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.agent import AgentFinish
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

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
        user_input = inputs.get("input", "")
        bot_response = outputs.get("output", "")
        self.conversation_history.append(bot_response)

    def clear(self):
        # Clear the stored conversation history
        self.conversation_history = []

custom_memory = CustomConversationMemory()
tools = create_tools()
functions = [convert_to_openai_function(f) for f in tools]
model = ChatOpenAI(temperature=0).bind(functions=functions)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful but sassy assistant"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Automatically receive when init agent executor
def run_agent(user_input):
    intermediate_steps = []
    while True:
        result = agent_executor.invoke({
            "input": user_input, 
            "intermediate_steps": intermediate_steps
        })
        if isinstance(result, AgentFinish):
            return result
        tool = {
            "search_wikipedia": search_wikipedia, 
            "search_online_products": search_online_products,
        }[result.tool]
        observation = tool.run(result.tool_input)
        intermediate_steps.append((result, observation))

agent_chain = RunnablePassthrough.assign(
    agent_scratchpad= lambda x: format_to_openai_functions(x["intermediate_steps"])
) | prompt | model | OpenAIFunctionsAgentOutputParser()
agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True)
# agent_executor.invoke({"input": "how to order an online product?"})
# agent_executor.invoke({"input": "mini cake"})

def run_with_memory(input_text):
    # Load conversation history and include in input
    memory_variables = custom_memory.load_memory_variables({"input": input_text})
    full_input = {"input": input_text, **memory_variables}

    # Run the conversation
    response = agent_executor.invoke(full_input)

    # Save context (user input and AI response)
    custom_memory.save_context({"input": input_text}, {"output": response})

    return response

# Test conversation
run_with_memory("how to order an online product?")
run_with_memory("mini cake")
run_with_memory("mousse")
