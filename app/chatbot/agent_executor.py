import logging
from app.chatbot.parser.agent_output_parser import LLMOutputParser
from dotenv import load_dotenv, find_dotenv
import os
import openai
from typing import Any

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import HumanMessage
from app.chatbot.memory.window_memory import ConversationBufferWindowMemory
from app.chatbot.tools.tools import create_tools
from langchain_community.chat_message_histories import ChatMessageHistory

def _handle_error(error) -> str:
    print("_handle_error_agent")
    return str(error)[:50]

# Define a global memory to avoid re-initializing for each query
window_memory = ConversationBufferWindowMemory(k=5)

class MainAgentChatbot:
    agent_executor: Any
    def __init__(self) -> None:
        tools = create_tools()
        functions = [convert_to_openai_function(f) for f in tools]
        model = ChatOpenAI(
            temperature=0.2, # Setting the temperature low (closer to 0) ensures that the responses are more deterministic and less random, which is ideal when handling product-related queries, pricing, and other factual information
            model="gpt-4o-mini", 
            streaming=True,
            max_tokens=300, # Limiting the tokens to 256–512 ensures the responses are clear and not too verbose, especially when summarizing product details
            # timeout=5, # A 5 to 10 seconds timeout ensures a balance between responsiveness and allowing the model sufficient time to generate accurate responses.
            # max_retries=3 # Increasing max_retries to 3 allows the system to try a couple more times if it encounters a transient issue, ensuring better uptime and response consistency.
        ).bind(functions=functions)

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

        ### Few shots samples:
        #### Sample 1:
        - Question: "Tell me about order process"
        - Thought: The question asks for order process, so I will use `search_on_local_assets` to find order process.
        - Action: search_on_local_assets
        - Action Input: "order process"
        - Observation: The order process involves browsing and selecting products, adding them to the cart, proceeding to checkout, entering shipping and billing information, choosing a payment method, reviewing and confirming the order, and finally placing the order successfully.
        - Thought: I found full information about order process, I will summarize that information and give the concise answer
        - Final Answer: "The order process involves browsing and selecting products, adding them to the cart, proceeding to checkout, entering shipping and billing information, choosing a payment method, reviewing and confirming the order, and finally placing the order successfully."
        
        #### Sample 2:
        - Question: "What is the price of a Black Forest Cake"
        - Thought: The question asks for product information, so I will use `search_sql_data` to find order process.
        - Action: search_sql_data
        - Action Input: price of a Black Forest Cake"
        - Observation: I found one product related to Black Forest Cake:
        + Price: 18.99
        + Title: Black Forest Cake
        + Description: Decadent chocolate cake layered with cherries and whipped cream.
        - Thought: I now have the price of the Black Forest Cake, I will summarize that information and give the accurate answer
        - Final Answer: "The price of the Black Forest Cake is 18.99"

        #### Sample 3:
        - Question: "What is the price of a Black Forest Cake and what is the return policy for this item?"
        - Thought: The question asks for product information and a return policy. I should first use `search_sql_data` to find the Black Forest Cake price, then use `search_on_local_assets` to find the return policy.
        - Action: search_sql_data
        - Action Input: "Price of Black Forest Cake"
        - Observation: I found one product related to Black Forest Cake:
        + Price: 18.99
        + Title: Black Forest Cake
        + Description: Decadent chocolate cake layered with cherries and whipped cream.
        - Thought: I now have the price of the Black Forest Cake. Next, I need to find the return policy, so I'll use the `search_on_local_assets` tool.
        - Action: search_on_local_assets
        - Action Input: "return policy"
        - Observation: Returns are accepted within 30 days of purchase. The product must be in its original condition and packaging.
        - Thought: I now know the return policy. I will combine this information with the price, title and description of the Black Forest Cake to provide a complete answer.
        - Final Answer: "The price of the Black Forest Cake is 18.99. Decadent chocolate cake layered with cherries and whipped cream. The return policy allows returns within 30 days of purchase, as long as the product is in its original condition and packaging."

        #### Sample 4:
        - Question: "What is LangChain?"
        - Thought: The question is not relevant to e-commerce or product, hence I will use search_wikipedia to seek the results.
        - Action: search_wikipedia
        - Action Input: "What is LangChain?"
        - Observation: LangChain is a software framework that helps facilitate the integration of large language models (LLMs) into applications. Its use-cases include document analysis and summarization, chatbots, and code analysis.
        - Thought: I now know about LangChain. I will combine the answer.
        - Final Answer: "LangChain is a software framework that helps facilitate the integration of large language models (LLMs) into applications. Its use-cases include document analysis and summarization, chatbots, and code analysis."

        Begin!

        Question: {input}
        Previous conversation history: {chat_history}
        Thought:{agent_scratchpad}
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        llm_parser = LLMOutputParser()
        react_agent = create_react_agent(
            llm=model,
            prompt=prompt,
            tools=tools,
            output_parser=llm_parser,
        ) 
        
        agent_executor = AgentExecutor(
            agent=react_agent, 
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
            memory=window_memory,
            max_iterations = 5, # useful when agent is stuck in a loop
        )
        self.agent_executor = agent_executor

    def run_with_memory(self, input_text, callback):
        # Load conversation history and include in input
        memory_variables = window_memory.load_memory_variables(input_text)
        full_input = {"input": input_text, **memory_variables}
        
        if callback is not None:
            chain_with_callbacks = self.agent_executor.with_config(callbacks=[callback])

            # Run the conversation
            response = chain_with_callbacks.invoke(full_input)
        else:
            response = self.agent_executor.invoke(full_input)
        # logging.info(response)
        return response

# Test conversation
# run_with_memory("How to order an online product?")
# run_with_memory("What is langchain?")
# run_with_memory("mini cake")
# run_with_memory("mousse")
# run_with_memory("order process")
