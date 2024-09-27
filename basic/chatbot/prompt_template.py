import os
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain import hub
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from chatbot.output_parser import CustomizeRouterOutputParser

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
tool = WikipediaQueryRun(api_wrapper=api_wrapper)
tools = [tool]
hub_prompt = hub.pull("hwchase17/react")

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

prompt_infos = [
    {
        "name": "faqs", 
        "description": "Good for answering questions about faqs", 
        "prompt_template": faqs_template
    },
    {
        "name": "order process", 
        "description": "Good for answering order process questions", 
        "prompt_template": order_process_template
    },
    {
        "name": "product information", 
        "description": "Good for answering product information questions", 
        "prompt_template": products_information_template
    },
    {
        "name": "returns and refunds", 
        "description": "Good for answering returns and refunds questions", 
        "prompt_template": returns_and_refunds_template
    },
    {
        "name": "shipping information", 
        "description": "Good for answering shipping information questions", 
        "prompt_template": shipping_info_template
    }
]

class CustomAgentExecutor(AgentExecutor):
    @property
    def output_keys(self) -> List[str]:
        return ["text"]

    def run(self, input: Any, **kwargs: Any) -> Dict[str, Any]:
        result = super().run(input, **kwargs)
        return {"text": result["output"]}

# class AgentLLMChain(LLMChain):
#     agent_executor: AgentExecutor

#     def __init__(self, agent_executor: AgentExecutor, **kwargs: Any):
#         self.agent_executor = agent_executor
#         super().__init__(**kwargs)

#     def run(self, input: Any, **kwargs: Any) -> Dict[str, Any]:
#         return self.agent_executor.run(input, **kwargs)

def _handle_error(error) -> str:
    print("_handle_error")
    return str(error)[:50]

def initialize_model():
    llm = ChatOpenAI(temperature=0.9, model="gpt-3.5-turbo")
    # default_prompt = ChatPromptTemplate.from_template("{input}")
    # default_chain = default_prompt | llm | StrOutputParser()

    destination_chains = {}
    for p_info in prompt_infos:
        name = p_info["name"]
        prompt_template = p_info["prompt_template"]
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        first_chain = LLMChain(llm=llm, prompt=prompt)
        # Error: Agent executor doesn't work with MultiPromptChain
        # agent_executor = CustomAgentExecutor(
        #     agent=create_react_agent(first_chain, tools, hub_prompt),
        #     tools=tools,
        #     verbose=True,
        #     handle_parsing_errors=_handle_error
        # )
        destination_chains[name] = first_chain
        
    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)

    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=CustomizeRouterOutputParser(),
    )

    router_chain = LLMRouterChain.from_llm(llm, router_prompt)
    chain = MultiPromptChain(router_chain=router_chain, 
                            destination_chains=destination_chains, 
                            default_chain=destination_chains['faqs'], 
                            verbose=True
                            )
    return chain
