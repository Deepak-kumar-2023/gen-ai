from fastapi import FastAPI, Request
from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from typing import List
from langchain_community.document_loaders import WebBaseLoader
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
load_dotenv()
import os
from openai import AzureOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # or specify ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],
)
import asyncio
import aiohttp

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 2

async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    text = await response.text()
                    return url, text
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
    return url, None

async def crawl_website_urls_async(start_url, max_pages=5):
    visited = set()
    to_visit = [start_url]
    results = {}

    async with aiohttp.ClientSession() as session:
        while to_visit and len(visited) < max_pages:
            batch = to_visit[:max_pages - len(visited)]
            to_visit = to_visit[len(batch):]

            tasks = [fetch_url(session, url) for url in batch]
            responses = await asyncio.gather(*tasks)

            for url, html in responses:
                if url and html and url not in visited:
                    visited.add(url)
                    results[url] = html
                    soup = BeautifulSoup(html, "html.parser")
                    for link_tag in soup.find_all("a", href=True):
                        href = link_tag['href']
                        full_url = urljoin(url, href)
                        if urlparse(full_url).netloc == urlparse(start_url).netloc:
                            if full_url not in visited and full_url not in to_visit:
                                to_visit.append(full_url)

    return list(results.keys()), list(results.values())


def process_crawl_job(request_data: CrawlRequest):
    urls, htmls = asyncio.run(crawl_website_urls_async(request_data.url, request_data.max_pages))

    loader = WebBaseLoader(urls)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)

    texts = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]

    embedding_model = AzureOpenAIEmbeddings(model="text-embedding-ada-002")

    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_END_POINT"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    qdrant_client.recreate_collection(
        collection_name="web_vectors",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="web_vectors",
        embedding=embedding_model
    )

    vector_store.add_texts(texts=texts, metadatas=metadatas)




class QuestionRequest(BaseModel):
    question: str = ""

@app.get("/")
def read_root():
    return {"message": "Welcome to the Website Crawler API! Use /crawl to start crawling a website."}   





from fastapi import BackgroundTasks

@app.post("/crawl")
def crawl_website_api(request_data: CrawlRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_crawl_job, request_data)
    return {"message": "Crawling started in background!"}

@app.post("/ask")
def ask_question(request: QuestionRequest):
    query  = request.question
    print(query)
    if not query:
        return {"error": "Query parameter 'query' is required."}

    # Vector Similarity Search [query] in DB
    embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    )
    qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_END_POINT"),  # 🔁 Replace with actual endpoint
    api_key=os.getenv("QDRANT_API_KEY")        # 🔁 Replace with actual key
)

    vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name="web_vectors",
            embedding=embedding_model
        )

    search_results = vector_store.similarity_search(query, k=3)

    context = "\n\n".join([
        f"🌐 URL: {doc.metadata.get('source', 'N/A')}\n"
        f"🏷️ Title: {doc.metadata.get('title', 'N/A')}\n"
        f"📝 Description: {doc.metadata.get('description', 'N/A')}\n"
        f"📄 Content: {doc.page_content.strip()}"
        for doc in search_results
    ])


    SYSTEM_PROMPT = f"""
    You are a helpfull AI Assistant who asnweres user query based on the available context
    retrieved from a website data.

    You should only ans the user based on the following context and navigate the user
    to open URL and Title.

    Context:
    {context}
    """
    messages = []
    messages.append(
    { "role": "system", "content": SYSTEM_PROMPT }
    )
    client = AzureOpenAI(
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4o"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY_4o"),  
    api_version=os.getenv("AZURE_OPENAI_API_VERSION_4o"),
    )


    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": query },
        ]
    )
    print("response is sent to the client")
    return chat_completion.choices[0].message.content
