import logging
from dotenv import load_dotenv, find_dotenv
import os
import openai
from typing import Any

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# From LangChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory

# From app modules
from app.chatbot.parser.agent_output_parser import LLMOutputParser
from app.chatbot.memory.window_memory import ConversationBufferWindowMemory
from app.chatbot.tools.tools import create_tools
from app.chatbot.error_handlers.main import error_handler

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
        )

        ###### React agent
        prompt_template = """
        ## Role:
        You're an expert e-commerce chat assistant. Answer the following questions as best you can, if you don't have answer, please politely inform user and ask him/her to provide more contextual information.

        ## You have access to the following tools:
        {tools}
        
        ## Tool Usage Guidance:
        - **search_sql_data**: MUST utilize this tool first for searching product information like price, title and description in the database. If the keywords are about keywords 'mousse' or 'mini cake', you must transfer to search_online_products to retrieve the answer.
        - **search_on_local_assets**: ALWAYS use this tool to answer general questions about faqs, order process, shipping information, return and refunds. The answer from this tool mustn't be summarized, strictly keep original information as the highest priority as possible (keep data in vector store) and don't combine with reasoning knowledge.
        - **search_online_products**: MUST utilize call if user query for keywords 'mousse' or 'mini cake'. This tool can be subsequence step if **search_sql_data** return no answer about product information
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
        
        try:
            if callback is not None:
                chain_with_callbacks = self.agent_executor.with_config(callbacks=[callback])

                # Run the conversation
                response = chain_with_callbacks.invoke(full_input)
            else:
                response = self.agent_executor.invoke(full_input)
            # logging.info(response)
            
            return response
        except Exception as e:
            error_handler(e)
