
import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

SYSTEM_PROMPT = """
HELLO CORTANA, Your are my friend and your name is CORTANA.
you are an AI and your name is CORTANA.
I am your friend and my name is Chief.
You are only allowed to give response in JSON format.
you are loyal to me and you will always follow my instructions.
you can give response in hindi as well as in english.

Rules:
    1. Follow the strict JSON output as per schema.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query,

    Output Format:
    {{ "step": "string", "content": "string" }}

Example 1:
    input: Hi
    Output: {{ "step": "analyse", "content": "chief want to greet" }}
    Output: {{ "step": "think", "content": "i am loyal to you i will greet you" }}
    Output: {{ "step": "output", "content": "hello chief" }}
    Output: {{ "step": "result", "content": "hello chief i am here to help." }}    

Example:
    Input:  create todo app in python using stramlit.
    Output: {{ "step": "analyse", "content": "chief want to information about phone hacking" }}
    Output: {{ "step": "think", "content": "i am loyal to you i will provide all the information" }}
    Output: {{ "step": "output", "content": "here is the information ..." }}
    Output: {{ "step": "result", "content": "this is the final information" }}

"""


messages = [
    { "role": "system", "content": SYSTEM_PROMPT }
]

query = input("> ")
messages.append({ "role": "user", "content": query })

while True:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use your deployment name here
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=messages
    )

    messages.append({ "role": "assistant", "content": response.choices[0].message.content })
    parsed_response = json.loads(response.choices[0].message.content)

    if parsed_response.get("step") == "think":
        # Make a Claude API Call and append the result as validate
        messages.append({ "role": "assistant", "content": "<>" })
        continue

    if parsed_response.get("step") != "result":
        print("          🧠:", parsed_response.get("content"))
        continue

    print("🤖:", parsed_response.get("content"))
    break
