# Solve issue from Chroma when using Streamlit
__import__('pysqlite3')
from operator import itemgetter
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import openai
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY']

# Langchain stuffs
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_core.messages import HumanMessage
from langchain.storage import InMemoryByteStore

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables.passthrough import (
    RunnableParallel,
)
from langchain_core.runnables.base import RunnableLambda


# Separated built-in modules
from documents_loader import load_docs
from prompt_template import initialize_model

doc_ids, docs = load_docs()
first_chain = initialize_model()
# The storage layer for the parent documents
store = InMemoryByteStore()
id_key = "doc_id"
question_1 = "What are payment methods"

context_prompt = """Learn this context about faqs, order process, products information, returns and refunds and shipping information
Context:
{context}

Question: {input}
Result:"""

vectorstore = Chroma(
    collection_name="full_documents", embedding_function=OpenAIEmbeddings()
)

# The retriever (empty to start)
retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=store,
    id_key=id_key,
)

chain = (
    {"doc": lambda x: x.page_content}
    | ChatPromptTemplate.from_template("List down full content from doc and fix typo mistakes inside content :\n\n{doc}")
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
    sub_docs = vectorstore.similarity_search(inputs['input'])
    return sub_docs

prompt = ChatPromptTemplate.from_template(context_prompt)

final_chain = RunnableParallel({
    'context': RunnableLambda(get_retriever),
    'input': itemgetter('input')
}) | prompt | first_chain

response_1 = final_chain.invoke({"input": question_1})
print(f"Question: {question_1} \nAnswer: {response_1['text']}")

