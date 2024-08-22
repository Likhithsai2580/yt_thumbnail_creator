import os
import json
from groq import Groq
import time

api_key = os.getenv("GROQ_API_KEY")

client = Groq(
# This is the default and can be omitted
api_key=api_key,
)

def LLM(messages: list, message: str, role: str):
    time.sleep(5)
    # Append user message to messages list
    messages.append({"role": role, "content": message})

    # Create client and get response
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192"
        )
        # Extract assistant message from response
        ms = chat_completion.choices[0].message.content

        # Append assistant message to messages list
        messages.append({"role": "assistant", "content": ms})

        return ms
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
