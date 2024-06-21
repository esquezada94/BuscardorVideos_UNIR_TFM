from openai import OpenAI
from dotenv import load_dotenv
import os, json

load_dotenv('.env')

def init_openai():
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    return client

def completion_openai(client, model, messages):
    response = client.chat.completions.create(
        model = model,
        messages = messages
    )
    return response.choices[0].message.content.strip(), response.usage

def tool_openai(client, model, messages, tools):
    response = client.chat.completions.create(
        model = model,
        messages = messages,
        tools = tools,
        tool_choice = "auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
        
    return function_name, function_args, response.usage