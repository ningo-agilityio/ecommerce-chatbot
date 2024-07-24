from typing import Iterator
import uuid

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CustomDocumentLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:  # <-- Does not take any arguments
        """A lazy loader that reads a file line by line.

        When you're implementing lazy load methods, you should use a generator
        to yield documents one by one.
        """
        with open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={"line_number": line_number, "source": self.file_path},
                )
                line_number += 1

def load_docs():
    loaders = [
        CustomDocumentLoader("assets/faqs.txt"),
        CustomDocumentLoader("assets/order-process.json"),
        CustomDocumentLoader("assets/products-information.txt"),
        CustomDocumentLoader("assets/returns-and-refunds.csv"),
        CustomDocumentLoader("assets/shipping-info.txt"),
        
    ]
    docs = []
    for loader in loaders:
        docs.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000)
    docs = text_splitter.split_documents(docs)
    doc_ids = [str(uuid.uuid4()) for _ in docs]

    return doc_ids, docs

doc_ids, docs = load_docs()
print(doc_ids[0], docs[0])