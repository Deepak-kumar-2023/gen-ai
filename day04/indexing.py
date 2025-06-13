from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import InMemoryVectorStore
import os
import getpass

load_dotenv()

pdf_path = Path(__file__).parent / "study.pdf"

# Loading
loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load() # Read PDF File

# Chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024,  # Size of each chunk
    chunk_overlap=400
)



split_docs = text_splitter.split_documents(documents=docs)

embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    
)

# Using [embedding_model] create embeddings of [split_docs] and store in DB

vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Indexing of Documents Done...")



