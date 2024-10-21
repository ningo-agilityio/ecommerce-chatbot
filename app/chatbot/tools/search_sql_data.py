import logging
from typing import Any
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_community.agent_toolkits import create_sql_agent

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

from database.documents import init_products

class QueryProductsSQLDataService:
  chain: Any
  def __init__(self) -> None:
    # Init product before executing
    init_products()

    db = SQLDatabase.from_uri("sqlite:///ecommerce_chatbot.db")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, 
        answer the user question about product information especially cake details 
        namely title (name), description, price

        Question: {input}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
    )
    answer = answer_prompt | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent=chain,
        verbose=True,
        agent_type="openai-tools"
    )
    self.chain = agent_executor
  def search(self, query):
    response = self.chain.invoke({"input": query})
    return response