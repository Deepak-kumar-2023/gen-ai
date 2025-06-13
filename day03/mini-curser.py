import json
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import requests
load_dotenv()
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)


def run_command(cmd: str):
    result = os.system(cmd)
    return result

def get_weather(city: str):
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    
    return "Something went wrong"


available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}





SYSTEM_PROMPT = """
You are Cortana your name is CORTANA. you are a helpful AI assistant.
You are designed to assist users in a step-by-step manner, providing clear and concise responses based on the user's queries. Your responses should be structured in strict JSON format as per the schema provided below.
You will analyze the user's query, think through the problem, and provide a final result based on your analysis. Each step should be clearly defined and should follow the rules outlined below.

    You work on start, plan, action, observe mode.

    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.

    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}

    Available Tools:
    - "get_weather": Takes a city name as an input and returns the current weather for the city
    - "run_command": Takes linux command as a string and executes the command and returns the output after executing it.

    Example:
    User Query: What is the weather of new york?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}



Rules:
    1. Follow the strict JSON output as per schema.
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query,

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}



Example:
    Input: create a todo app in python
    Output: {{ "step": "plan", "content": "The user wants to create a todo app in Python" }}
    Output: {{ "step": "plan", "content": "To create a todo app in Python, we need to consider the following steps: 1. Define the requirements for the todo app. 2. Choose a framework or library for building the app. 3. Design the user interface. 4. Implement the backend logic. 5. Test the app." }}
    Output: {{ "step":"plan":"1. first i will create an input box for taking a todo, 2. then i will create a box for showing all the todo, 3. then i will create a delete button for deleting the individual todo." }}
    Output: {{ "step": "plan", "content": "for creating an todo app i will use streamlit framework, Now i will design an interface for todo. there will be an input box for taking a todo , one box for showing all the todo. one delete button for deleting the invidual todo." }}
    OutPut: {{ "step":"action", "function": "run_command", "input": "pip install streamlit" }}
    Output: {{ "step": "action", "function": "run_command","input" : "touch todo.py" }}
    Output: {{ "step": "plan", "content":   "file is created sucessfully. i have to add all the necessary import statement" }}
    Output: {{ "step": "action", "function": "run_command", "input": "echo \"import streamlit as st\" > todo.py" }}
    Output: {{ "step": "plan", "content": "Now i will add the code for taking input from user and showing all the todo" }}
    Output: {{ "step": "action", "function": "run_command", "input": "echo \"new_task = st.text_input("Enter a new task", placeholder="e.g., Complete assignment") \" >> todo.py" }}
    Output: {{ "step": "action", "function": "run_command", "input": "echo \"
        if "tasks" not in st.session_state:
            st.session_state.tasks = []
        # Add button to store input
        if st.button("Add Task"):
            if new_task.strip():
                st.session_state.tasks.append(new_task.strip())
    \" >> todo.py" }}
    Output: {{ "step": "action", "function": "run_command", "input": "echo \"

st.subheader("Your Tasks:")
for i, task in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(f"{i+1}. {task}")
    with col2:
        if st.button("Delete", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()  # Refresh the app to reflect changes
    
    
    \" >> todo.py" }}

    
    Output: {{ "step": "action", "function": "run_command", "input": "streamlit run todo.py" }}

"""

messages = [
  { "role": "system", "content": SYSTEM_PROMPT }
]

while True:
    query = input("> ")
    messages.append({ "role": "user", "content": query })

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=messages
        )

        messages.append({ "role": "assistant", "content": response.choices[0].message.content })
        parsed_response = json.loads(response.choices[0].message.content)

        if parsed_response.get("step") == "plan":
            print(f"🧠: {parsed_response.get("content")}")
            continue

        if parsed_response.get("step") == "action":
            tool_name = parsed_response.get("function")
            tool_input = parsed_response.get("input")

            print(f"🛠️: Calling Tool:{tool_name} with input {tool_input}")

            if available_tools.get(tool_name) != False:
                output = available_tools[tool_name](tool_input)
                messages.append({ "role": "user", "content": json.dumps({ "step": "observe", "output": output }) })
                continue
        
        if parsed_response.get("step") == "output":
            print(f"🤖: {parsed_response.get("content")}")
            break







