from langchain_openai import AzureOpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
load_dotenv()
# 
from langchain_community.document_loaders import WebBaseLoader
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# def crawl_website_urls(start_url, max_pages=2):
#     visited = set()
#     to_visit = [start_url]

#     while to_visit and len(visited) < max_pages:
#         url = to_visit.pop(0)
#         if url in visited:
#             continue

#         try:
#             print(f"🔍 Crawling: {url}")
#             response = requests.get(url, timeout=10)
#             visited.add(url)

#             if "text/html" not in response.headers.get("Content-Type", ""):
#                 continue

#             soup = BeautifulSoup(response.text, "html.parser")

#             for link_tag in soup.find_all("a", href=True):
#                 href = link_tag['href']
#                 full_url = urljoin(url, href)

#                 # Same domain only
#                 if urlparse(full_url).netloc == urlparse(start_url).netloc:
#                     if full_url not in visited and full_url not in to_visit:
#                         to_visit.append(full_url)

#         except Exception as e:
#             print(f"❌ Failed to crawl {url}: {e}")
#             continue

#     return list(visited)

# start_url = "https://docs.chaicode.com/youtube/chai-aur-git/branches//"  # Replace with your target site
# crawled_data = crawl_website_urls(start_url)

# loader = WebBaseLoader(
#     crawled_data
# )

# docs = loader.load()

# print("docs", docs)

# for page in crawled_data:
#     print("\n📄 Page:", page["url"])
#     print("📜 Text preview:", page["text"], "...\n")


# splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# chunks = splitter.split_documents(crawled_data)

# Step 3: Embed chunks
embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
    
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="web_vectors",
    embedding=embedding_model
)

query = "What is html?"

search_results = vector_db.similarity_search(query, k=3)

context = "\n\n".join([
    f"🌐 URL: {doc.metadata.get('source', 'N/A')}\n"
    f"🏷️ Title: {doc.metadata.get('title', 'N/A')}\n"
    f"📝 Description: {doc.metadata.get('description', 'N/A')}\n"
    f"📄 Content: {doc.page_content.strip()}"
    for doc in search_results
])

   


print(context)