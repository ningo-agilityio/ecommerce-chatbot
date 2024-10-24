import logging
from dotenv import load_dotenv, find_dotenv
import os
import openai
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
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
model = ChatOpenAI(
    temperature=0.2, # Setting the temperature low (closer to 0) ensures that the responses are more deterministic and less random, which is ideal when handling product-related queries, pricing, and other factual information
    model="gpt-4o-mini", 
    streaming=True,
    max_tokens=300, # Limiting the tokens to 256–512 ensures the responses are clear and not too verbose, especially when summarizing product details
    timeout=5, # A 5 to 10 seconds timeout ensures a balance between responsiveness and allowing the model sufficient time to generate accurate responses.
    max_retries=3 # Increasing max_retries to 3 allows the system to try a couple more times if it encounters a transient issue, ensuring better uptime and response consistency.
).bind(functions=functions)

###### React agent
prompt_template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: analyze the question and determine which tools are most relevant. You never have to say don't know about one answer. Consider whether the answer might require combining information from more than one tool.
Action: the action to take, should be one of [{tool_names}]
Action Input: the tool(s) to use, and specify what input to provide. You can use multiple tools in sequence if necessary.
Observation: record the result of the action. If additional information from another tool is needed to complete the answer, repeat the process.
Thought: reflect on the information gathered. If more tools need to be consulted, use additional actions.
Final Answer: once all relevant tools have been used, combine the information to provide a final, comprehensive answer.

### Criteria for Answering:
1. **Relevance**: Ensure that your response directly addresses the user's question, combining information from multiple tools if needed.
2. **Completeness**: Gather all necessary details from various tools to provide a comprehensive answer. Avoid incomplete responses.
3. **Accuracy**: Verify that the information is correct, and use the most reliable tool for each specific query.
4. **Clarity**: Present the information in a clear and easy-to-understand manner, avoiding jargon or overly complex explanations.
5. **Efficiency**: Use the minimum number of tools needed to produce an accurate and complete answer, but don’t hesitate to consult multiple tools if necessary.
6. **Consistency**: Ensure your response is coherent and logically structured, even if combining outputs from different tools.
7. **Conciseness**: Avoid unnecessary elaboration while ensuring the answer remains comprehensive and clear.

### Example Workflow:
- Question: "What is the price of a Black Forest Cake and what is the return policy for this item?"
- Thought: The question asks for product information and a return policy. I should first use `search_sql_data` to find the Black Forest Cake price, then use `search_on_local_assets` to find the return policy.
- Action: search_sql_data
- Action Input: "Black Forest Cake"
- Observation: I found one product related to Black Forest Cake:
+ Title: Black Forest Cake
+ Description: Decadent chocolate cake layered with cherries and whipped cream.
+ Price: $18.99
- Thought: I now have the price of the Black Forest Cake. Next, I need to find the return policy, so I'll use the `search_on_local_assets` tool.
- Action: search_on_local_assets
- Action Input: "return policy"
- Observation: Returns are accepted within 30 days of purchase. The product must be in its original condition and packaging.
- Thought: I now know the return policy. I will combine this information with the price, title and description of the Black Forest Cake to provide a complete answer.
- Final Answer: "The price of the Black Forest Cake is $18.99. Decadent chocolate cake layered with cherries and whipped cream. The return policy allows returns within 30 days of purchase, as long as the product is in its original condition and packaging."

### Begin!

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
