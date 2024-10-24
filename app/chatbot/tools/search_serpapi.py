from typing import Any
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents import AgentExecutor, create_react_agent

prompt_template = """
Search results from Google engine with quick response.
You never have to say don't know to any answer, you can search and give a combined answer from multiple agents sources.

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

### Example Workflow:
Question: Search for Samsung Galaxy S23 Ultra
Final Answer:
**Title**: Samsung Galaxy S23 Ultra 5G Dual S918b 256gb 8GB RAM GSM Unlocked Green, Size: 6.8 x 3.07 x 0.35
**Price**: $849.99
**Thumbnail**: https://serpapi.com/searches/6719b775a5d702c288b265a7/images/4320d4e57226a38828246d566cc6431baad4018983dc7285f8cf795f9a1e3d5d.webp

### Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
model = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True)

class SerpAPIService:
  serpapi_agent: Any

  def __init__(self) -> None:
    tools = load_tools(["serpapi"])
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
    self.serpapi_agent = agent_executor
    # ISSUE: we need to parse result from this wrapper
    # self.serpapi = SerpAPIWrapper()

  def search(self, query):
    return self.serpapi_agent.invoke({"input": query})