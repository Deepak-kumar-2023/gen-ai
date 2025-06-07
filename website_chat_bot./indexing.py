from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_qdrant import QdrantVectorStore
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import WebBaseLoader
load_dotenv()


# Step 1: Load website content
loader = WebBaseLoader(
    "https://docs.chaicode.com/youtube/chai-aur-git/branches/",
)
docs = loader.load()

# Step 2: Split content
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# Step 3: Embed chunks
embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    
)

vectorstore = FAISS.from_documents(chunks, embedding_model)

# Step 4: Search + Chat
retriever = vectorstore.as_retriever()
results = retriever.invoke("Tell me something about parrots.")
print(results[0].page_content)



