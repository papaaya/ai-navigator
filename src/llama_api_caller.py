from llama_api_client import LlamaAPIClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = LlamaAPIClient()

response = client.chat.completions.create(
  model="Llama-4-Maverick-17B-128E-Instruct-FP8",
  messages=[
    {"role": "user", "content": "Hello, how are you?"}
  ],
  max_completion_tokens=1024,
  temperature=0.7,
)

print(response)