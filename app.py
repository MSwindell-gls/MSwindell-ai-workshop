import os
from openai import AzureOpenAI #<-- OpenAI SDK.  An alternate SDK would be Azure AI Inference SDK = azure-ai-inference = https://learn.microsoft.com/en-us/python/api/overview/azure/ai-inference-readme?view=azure-python-preview
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Make a simple request

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),  # Use env var with fallback
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! What's the weather like?"}
    ],
    max_tokens=100
)

# Print the response
print(response.choices[0].message.content)