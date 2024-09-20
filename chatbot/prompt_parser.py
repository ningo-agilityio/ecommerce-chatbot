# Solve issue from Chroma when using Streamlit
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from operator import itemgetter
import os
from typing import Any, Optional
import openai
# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv())
# openai.api_key = os.environ['OPENAI_API_KEY']

# Langchain stuffs
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables.passthrough import (
    RunnablePassthrough
)
from langchain_core.runnables.base import RunnableLambda

# Separated built-in modules
from chatbot.documents_loader import load_docs
from chatbot.prompt_template import initialize_model

def initialize_chain():
    doc_ids, docs = load_docs()
    first_chain = initialize_model()
    # The storage layer for the parent documents
    store = InMemoryByteStore()
    id_key = "doc_id"

    context_prompt = """Learn this context about faqs, order process, products information, returns and refunds and shipping information
    Context:
    {context}
    
    Chat history: {chat_history}

    Question: 
    {input}
    Result:"""

    vector_store = Chroma(
        collection_name="full_documents", embedding_function=OpenAIEmbeddings()
    )

    # The retriever (empty to start)
    retriever = MultiVectorRetriever(
        vectorstore=vector_store,
        byte_store=store,
        id_key=id_key,
    )

    chain = (
        {"doc": lambda x: x.page_content}
        | ChatPromptTemplate.from_template("{doc}")
        | ChatOpenAI(max_retries=0)
        | StrOutputParser()
    )

    outputs_samples = chain.batch(docs, {"max_concurrency": 5})
    outputs_samples_docs = [
        Document(page_content=s, metadata={id_key: doc_ids[i]})
        for i, s in enumerate(outputs_samples)
    ]
    retriever.vectorstore.add_documents(outputs_samples_docs)
    retriever.docstore.mset(list(zip(doc_ids, docs)))

    def get_retriever(inputs):
        sub_docs = vector_store.similarity_search(inputs['input'])
        context_content = [f"{doc.page_content}" for doc in sub_docs]
        # return ("\n".join(context_content)).replace('"', "\'")
        return ("\n".join(context_content))

    # Context prompt
    prompt = ChatPromptTemplate.from_template(context_prompt)

    return RunnablePassthrough.assign(context=RunnableLambda(lambda x: get_retriever(x))) | prompt | first_chain
