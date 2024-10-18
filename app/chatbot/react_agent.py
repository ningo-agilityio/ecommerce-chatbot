import logging
from typing import Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents.format_scratchpad import format_to_openai_functions

import os
import openai
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']


class TestReactAgent:
    chain: Any
    def __init__(self) -> None:
        react_agent_prompt_template = """
        You are a smart AI assistant that can help with different types of e-commerce queries.
        You can use the context given to you to answer the question.
        You have access to the following tools:

        {tools}
        When providing an answer, ensure to return only one of the following:
        \n\n\n
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}
        """

        order_process_template = """You are great at answering ecommerce order process questions. \
        You can list down step by step in order and mention about payment methods \
        then put them together to answer accurately the broader question.

        When you don't know the answer to a question you admit\
        that you don't know.

        Here is a question:
        {input}"""

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
        
        order_process = Tool(
            name="order_process",
            func=lambda x: order_process_template.format(input=x) if x else "I don't know.",
            description="Useful for showing order process",
        )
        
        react_agent_prompt = ChatPromptTemplate.from_messages([
            ("system", react_agent_prompt_template),
            ("user", "{input}")
        ])
        react_agent = create_react_agent(llm, [order_process], react_agent_prompt)
        agent_executor = AgentExecutor(
            agent=react_agent, 
            tools=[order_process],
            verbose=True,
            handle_parsing_errors=True,
            max_iterations = 5 # useful when agent is stuck in a loop
        )
        self.chain = agent_executor
    def invoke(self, query):
        # Run the agent with dynamic routing based on the ReAct prompt
        return self.chain.invoke({
            "input": query,
        })
    
class ReactAgentForLocalAssetsRouting:
    chain: Any
    prompt_routing_tools: List
    def __init__(self) -> None:
        react_agent_prompt_template = """
        You are a smart AI assistant that can help with different types of e-commerce queries.
        You can use the context given to you to answer the question.
        You have access to the following tools:

        {tools}
        When providing an answer, ensure to return only one of the following:
        \n\n\n
        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}
        """

        # Define the tools (e.g., for FAQs, Product Information, etc.)
        faqs_template = """You are a very good at FAQs \
        You are great at answering questions about available ecommerce FAQS\
        and easy to understand manner. \
        When you don't know the accurate answer to a question you admit\
        that you don't know.

        Here is a question:
        {input}"""

        order_process_template = """You are great at answering ecommerce order process questions. \
        You can list down step by step in order and mention about payment methods \
        then put them together to answer accurately the broader question.

        When you don't know the answer to a question you admit\
        that you don't know.

        Here is a question:
        {input}"""

        products_information_template = """You are a very good at product information. \
        You have an excellent knowledge of and understanding of people,\
        events and contexts from a range of product categories. \
        You have the ability to think, reflect, discuss and \
        evaluate product information.
        If there are no products available, you will search from search_online_products or search_sql_data tools. 

        Here is a question:
        {input}"""

        returns_and_refunds_template = """ You are a successful returns and refunds bot.\
        You have a passion for creativity, collaboration,\
        forward-thinking, confidence, strong problem-solving capabilities,\
        understanding of category, return window and condition, and excellent communication \
        skills. You are great at answering accurately returns and refunds questions. \
        You are so good because you know how to solve a problem by \
        describing the solution in imperative steps. 

        Here is a question:
        {input}"""

        shipping_info_template = """ You are an excellent shipping information assistant.\
        You have a good knowledge about shipping information. You are great at answering shipping questions. \
        You are so great to break down shipping options, shipping carriers and when will be free shipping and then put them together \
        in the answer 

        Here is a question:
        {input}"""

        react_agent_prompt = ChatPromptTemplate.from_messages([
            ("system", react_agent_prompt_template),
            ("user", "{input}")
        ])
        order_process = Tool(
            name="order_process",
            func=lambda x: order_process_template.format(input=x) if x else "I don't know.",
            description="Useful for showing order process",
        )
        faqs = Tool(
            name="faqs",
            func=lambda x: faqs_template.format(input=x),
            description="Great at answering questions about available e-commerce FAQS and easy to understand manner"
        )
        product_information = Tool(
            name="product_information",
            func=lambda x: products_information_template.format(input=x),
            description="Good at product information. You have an excellent knowledge of and understanding of people, events and contexts from a range of product categories. You have the ability to think, reflect, discuss and evaluate product information"
        )
        returns_and_refunds = Tool(
            name="returns_and_refunds",
            func=lambda x: returns_and_refunds_template.format(input=x),
            description="Good knowledge about shipping information. You are great at answering shipping questions. You are so great to break down shipping options, shipping carriers and when will be free shipping and then put them together in the answer"
        )
        shipping_information = Tool(
            name="shipping_information",
            func=lambda x: shipping_info_template.format(input=x),
            description="Excellent shipping information assistant. You have a good knowledge about shipping information. You are great at answering shipping questions. You are so great to break down shipping options, shipping carriers and when will be free shipping and then put them together"
        )
        prompt_routing_tools = [
            faqs,
            order_process,
            product_information,
            returns_and_refunds,
            shipping_information,
        ]
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

        react_agent = create_react_agent(
            llm=llm,
            prompt=react_agent_prompt,
            tools=prompt_routing_tools
        )
        agent_executor = AgentExecutor(
            agent=react_agent, 
            tools=prompt_routing_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations = 5 # useful when agent is stuck in a loop
        )
        
        self.chain = agent_executor 
        self.prompt_routing_tools = prompt_routing_tools 

    def invoke(self, query):
      # Run the agent with dynamic routing based on the ReAct prompt
      return self.chain.invoke({
          "input": query
      })
