from openai import OpenAI
from config import API_KEY, BASE_URL, MODEL


client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_llm(tools, messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=True,
    )
    return response.choices[0].message
