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

# Use deployment name from env with a sensible fallback
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-chat")

# =====================
# Global context (edit this to shape all responses)
# Provide domain info, tone, constraints, style guides, etc.
# Example:
# - Audience: Product managers at a fintech company
# - Tone: Concise, friendly, and actionable
# - Constraints: Cite assumptions, ask clarifying questions when needed
# - Domain: Focus on scheduling features and integration patterns
GLOBAL_CONTEXT = """
You are a helpful assistant a developer working at a small financial institution.
""".strip()
# =====================

# Build the system prompt with global context merged in one system message (so pruning keeps it)
base_system_prompt = "You are a helpful assistant."
if GLOBAL_CONTEXT:
    base_system_prompt += f"\n\nContext to follow for every response:\n{GLOBAL_CONTEXT}"

# Initialize conversation history with a system prompt that includes the global context
messages = [
    {"role": "system", "content": base_system_prompt}
]

# Keep the conversation within reasonable length to avoid context limit issues
def prune_messages(history, max_pairs=20):
    # Keep system + last N user/assistant pairs
    if not history:
        return history
    system = history[:1] if history[0].get("role") == "system" else []
    tail = history[-(2 * max_pairs):]
    return system + tail

print("Type 'exit' to quit.")
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("exit", "quit", "q"):
        break

    messages.append({"role": "user", "content": user_input})

    try:
        resp = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        assistant_reply = resp.choices[0].message.content
        print(f"Assistant: {assistant_reply}\n")

        messages.append({"role": "assistant", "content": assistant_reply})
        messages = prune_messages(messages, max_pairs=20)
    except Exception as e:
        print(f"Error: {e}")