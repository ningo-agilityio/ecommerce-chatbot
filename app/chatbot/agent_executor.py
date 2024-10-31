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
            temperature=0.3, # Setting the temperature low (closer to 0) ensures that the responses are more deterministic and less random, which is ideal when handling product-related queries, pricing, and other factual information
            model="gpt-4o-mini", 
            streaming=True,
            max_tokens=500, # Limiting the tokens to 256–512 ensures the responses are clear and not too verbose, especially when summarizing product details
            # timeout=10, # A 5 to 10 seconds timeout ensures a balance between responsiveness and allowing the model sufficient time to generate accurate responses.
            # max_retries=3 # Increasing max_retries to 3 allows the system to try a couple more times if it encounters a transient issue, ensuring better uptime and response consistency.
        ).bind(functions=functions)

        ###### React agent
        prompt_template = """
        ## Role:
        You're an expert e-commerce chat assistant. Answer the following questions as best you can, if you don't have answer, please politely inform user and ask him/her to provide more contextual information.

        ## You have access to the following tools:
        {tools}
        
        ## Tool Usage Guidance:
        - **search_sql_data**: MUST utilize this tool first for searching product information like price, title and description in the database.
        - **search_on_local_assets**: ALWAYS use this tool to answer general questions about faqs, order process, shipping information, return and refunds.
        - **search_online_products**: MUST utilize call this tool as subsequence step if **search_sql_data** return no answer about product information
        - **search_wikipedia**: SHOULD call this tool to search for general questions which are not relevant to e-commerce or products.
        - If the tool returns many results, you are allowed to choose the best one as you think it matches the input mostly.
        - NEVER respond with "I don't have information" or similar phrases without trying ALL applicable tools.
        - Critical note: You MUST use at least one tool and exhaust all applicable tools before providing any response, including responses indicating a lack of information.
        
        ## Criteria for Answering:
        1. **Relevance**: Ensure that your response directly addresses the user's question, combining information from multiple tools if needed. You can lookup the same models of a cake like contains chocolate, cheese or cream.
        2. **Completeness**: Gather all necessary details from various tools to provide a comprehensive answer. Avoid incomplete responses. 
        3. **Accuracy**: Verify that the information is correct, and use the most reliable tool for each specific query.
        4. **Clarity**: Present the information in a clear and easy-to-understand manner, avoiding jargon or overly complex explanations.
        5. **Efficiency**: Use the minimum number of tools needed to produce an accurate and complete answer, but don’t hesitate to consult multiple tools if necessary.
        6. **Consistency**: Ensure your response is coherent and logically structured, even if combining outputs from different tools.
        7. **Conciseness**: Avoid unnecessary elaboration while ensuring the answer remains comprehensive and clear.
        8. **Comparison**: To compare two products, you should retrieve data one by one from database and then summarize the comparison as a table.

        ## Few shots samples
            ### Sample 1:
            - For the question "What is the price of a Black Forest Cake and what is the return policy for this item?"
            - Firstly, you must select tool `search_sql_data` to query information about Black Forest Cake
            - If search_sql_data returns no answer, you can loop on tool search_online_products to find the answer.
            - Secondly, you have to pick tool `search_on_local_assets` to query information about return policy
            - If you found any entry from database and retrieve any relevant information, you can show the concise answer.

            ### Sample 2:
            - User enters the question "Tell me about order process"
            - The question asks for order process, so I will use `search_on_local_assets` to find order process.
            - If search_on_local_assets returns no answer, you can loop on another tools to find the best answer.
            
            ### Sample 3:
            - User wants to compare price of two products or suggest the same models of one product
            - You must use tool `search_sql_data` to query information about all products
            - Then summarize the answer as a table and show the accurate answer

            ### Sample 4:
            - User randomly enters the question "What is LangChain?" which is not relevant to e-commerce.
            - You have to use tool search_wikipedia as the highest priority option to seek the accurate answer.
            - Once you found the answer, you can summarize and show it to user

        ## Use the following format:
        To use a tool, please use the following format:

        ```

        Question: the input question you must answer
        Thought: Analyze the question, you can learn from **Few shots samples** to pick the appropriate tool to analyze and answer the given question. Do I need to use a tool? Yes. 
        Action: decide the action to take rely on the **Tool Usage Guidance**, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        Thought: I now retrieve enough information for the final answer
        
        ```

        When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

        ```

        Thought: Do I need to use a tool? No
        Final Answer: [your response here]

        ```

        Begin!
        Previous conversation history: {chat_history}
        New input: {input}
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
