
from typing import Any

# Solve issue from Chroma when using Streamlit
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Langchain stuffs
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.passthrough import (
    RunnablePassthrough
)
from langchain_core.runnables.base import RunnableLambda

# Separated built-in modules
from app.chatbot.documents_loader import load_docs
from app.chatbot.docs_prompt_routing import initialize_docs_routing

def initialize_chain():
    # Load from both local assets and database
    doc_ids, docs = load_docs()
    first_chain = initialize_docs_routing()
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"

    context_prompt = """Learn this context about faqs, order process, products information, returns and refunds and shipping information
    Context:
    {context}
    
    Question: 
    {input}
    Result:"""

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

    # Context prompt
    prompt = ChatPromptTemplate.from_template(context_prompt)

    return RunnablePassthrough.assign(context=RunnableLambda(lambda x: get_retriever(x))) | prompt | first_chain

class LookupLocalAssetsService:
  chain: Any
  def __init__(self) -> None:
    
    self.chain = initialize_chain()

  def search(self, query):
    return self.chain.invoke({
      "input": query,
    })
