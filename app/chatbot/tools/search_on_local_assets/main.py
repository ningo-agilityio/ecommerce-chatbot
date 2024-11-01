
import logging
from typing import Any

# Langchain stuffs
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables.passthrough import (
    RunnablePassthrough
)
from langchain_core.runnables.base import RunnableLambda
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain import hub

# Separated built-in modules
from app.chatbot.tools.search_on_local_assets.documents_loader import load_docs
from app.chatbot.tools.search_on_local_assets.docs_prompt_routing import initialize_docs_routing

def initialize_retriever_tool():
    doc_ids, docs = load_docs()
    store = InMemoryByteStore()
    id_key = "doc_id"
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())
   
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        byte_store=store,
        id_key=id_key,
    )

    retriever.vectorstore.add_documents(docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))

    tool_lookup_docs = create_retriever_tool(
        retriever=retriever,
        name="search_on_local_assets",
        description="Search local assets (from vector store) for faqs (FAQs), order processes, returns, refunds, or shipping information. Sources: faqs.txt, order-process.json, returns-and-refunds.csv, shipping-info.txt.",
    )
    
    return tool_lookup_docs

def initialize_chain():
    # Load from both local assets and database
    doc_ids, docs = load_docs()
    first_chain = initialize_docs_routing()

    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"

    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())
   
    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        byte_store=store,
        id_key=id_key,
    )

    retriever.vectorstore.add_documents(docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))

    def get_retriever(inputs):
        sub_docs = vector_store.similarity_search(inputs['input'])
        context_content = [f"{doc.page_content}" for doc in sub_docs]
        return ("\n".join(context_content))

    return RunnablePassthrough.assign(context=RunnableLambda(lambda x: get_retriever(x))) | first_chain

class LookupLocalAssetsService:
  chain: Any
  tool: Any
  agent_executor: Any
  def __init__(self) -> None:
    
    self.chain = initialize_chain()
    tool = initialize_retriever_tool()
    self.tool = tool
    # This will allow to test tool
    # llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini",)
    # prompt = hub.pull("hwchase17/openai-tools-agent")
    # agent = create_openai_tools_agent(llm, [tool], prompt)
    # self.agent_executor = AgentExecutor(agent=agent, tools=[tool])

  def search(self, query):
    return self.chain.invoke({
      "input": query,
    })
