import os
import sys
from typing import Any, Iterator, List
import uuid
sys.path.append('../')
from database.documents import init_and_retrieve_documents
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CustomDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""
    data_from_db: List = None

    def __init__(self, file_path: str, data_from_db) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        if (data_from_db is None):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.abspath(os.path.join(current_dir, file_path))
            self.file_path = file_path
        else:
            self.data_from_db = data_from_db

    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """
        if (self.data_from_db is None):
            with open(self.file_path, encoding="utf-8") as f:
                line_number = 0
                for line in f:
                    doc = Document(
                        page_content=line,
                        metadata={"line_number": line_number, "source": self.file_path},
                    )
                    yield doc
                    line_number += 1
        else:
            line_number = 0
            for record in self.data_from_db:
                doc = Document(
                    page_content=record[2],
                    metadata={"line_number": [0], "source": record[1]},
                )
                yield doc
                line_number += 1

def load_docs():
    records = init_and_retrieve_documents()
    loaders = [
        # Keep only FAQs in document
        CustomDocumentLoader("assets/faqs.txt", None),
        CustomDocumentLoader("", records),
    ]
    docs = []

    # Save data from FAQ doc into retriever
    for loader in loaders:
        doc = loader.load()
        docs.extend(doc)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    docs = text_splitter.split_documents(docs)
    doc_ids = [str(uuid.uuid4()) for _ in docs]
    return doc_ids, docs
