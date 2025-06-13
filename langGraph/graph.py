from typing_extensions import TypedDict
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
import os
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_4o"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY_4o"),  
  api_version=os.getenv("AZURE_OPENAI_API_VERSION_4o"),
)

# Define the state structure using TypedDict
class State(TypedDict):
    query: str
    llm_result: str | None


# defined node in the graph
def chat_bot(state: State):

    query = state['query']

    llm_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": query}
        ]
    )

    result = llm_response.choices[0].message.content
    state["llm_result"] = result

    return state

# Create the state graph
graph_builder = StateGraph(State)

# created a node in the graph
graph_builder.add_node("chat_bot", chat_bot)

# added edges to the graph
graph_builder.add_edge(START, "chat_bot")
graph_builder.add_edge("chat_bot", END)

graph = graph_builder.compile()


def main():
    user = input("> ")

    # Invoke the graph
    _state = {
        "query": user,
        "llm_result": None
    }

    graph_result = graph.invoke(_state)
    print("graph_result", graph_result)


main()