from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import os
from pathlib import Path
# from langchain.embeddings import AzureOpenAIEmbeddings
from openai import AzureOpenAI
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()
client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4o"), 
        api_key= os.getenv("AZURE_OPENAI_API_KEY_4o"),  
        api_version= os.getenv("AZURE_OPENAI_API_VERSION_4o")
)

# Vector Embeddings
embedding_model = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002",
)




# Step 0: Create message history with a single system prompt
messages = [
    {
        "role": "system",
        "content": """You are a helpfull AI Assistant who asnweres user query based on the available context
                retrieved from a PDF file along with page_contents and page number.

                You should only ans the user based on the following context and navigate the user
                to open the right page number to know more."""
    }
]

while True:
    query = input("🧠 Ask your question (or type 'exit' to quit): ")

    if query.lower() in ["exit", "quit", "q"]:
        print("👋 Exiting... Have a great day, Deepak bhai!")
        break

    # Search for similar chunks in vector DB
    search_results = vector_db.similarity_search(query, k=3)

    # Create the context from those results
    context = "\n\n".join([
        f"📄 Page Content: {result.page_content}\n📘 Page Number: {result.metadata.get('page_label', 'N/A')}\n📁 Source: {result.metadata.get('source', 'N/A')}"
        for result in search_results
    ])

    # Append user query with context into the conversation
    user_message = f"""Use the following context to answer:
        {context}
        Query: {query}
        """
    messages.append({"role": "user", "content": user_message})

    # Get AI response
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Extract response
    ai_response = chat_completion.choices[0].message.content
    print(f"\n🤖 GPT: {ai_response}\n")

    # Store AI's response in memory
    messages.append({"role": "assistant", "content": ai_response})

