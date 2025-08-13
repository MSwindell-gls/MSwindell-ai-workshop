# Azure AI Foundry Getting Started Guide

## Project Overview

This is a simple Python application that demonstrates how to connect to and interact with Azure AI Foundry (formerly Azure OpenAI Service). The app consists of a basic Python script (`app.py`) that:

- Connects to your Azure AI Foundry endpoint using API credentials
- Sends text prompts to deployed AI models (like GPT-4 or GPT-3.5-turbo)
- Receives and displays AI-generated responses
- Provides a foundation for building more complex AI-powered applications

This getting started project is perfect for:
- Learning Azure AI Foundry basics
- Testing your Azure AI deployment
- Understanding how to integrate AI models into Python applications
- Exploring different AI model capabilities and responses

The app serves as a stepping stone to more advanced projects like web APIs, RAG (Retrieval-Augmented Generation) systems, and voice-enabled AI agents.

## Prerequisites
- Azure account with an active subscription
- Python 3.7+ installed
- Azure AI Foundry access

## Step 1: Create an Azure AI Foundry Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure AI Foundry"
4. Click "Create" and fill in:
   - **Resource group**: Create new or select existing `RG-DEV-AI-Workshop`
   - **Name**: Choose a unique name (e.g., `AIF-DEV-MyFoundryName`)
   - **Region**: Select your preferred region.  Hint: `East US 2` has preview features
   - **Default project name**: Choose a project name.  For example: `AAIFP-DEV-Default`
5. Click Next on the remaining options. 
6. Click "Review + create" then "Create"

## Step 2: Deploy a Model

1. Once created, go to your Azure AI Foundry resource
2. Navigate to "Models + endpoints" in the left menu
3. Click Deploy model
3. Choose an OpenAI model (e.g., "gpt-4" or "gpt-35-turbo")
4. Click "Confirm" then click Deploy
5. After Deployment completes, note down:
   - **Endpoint URL**: Something like `https://aaif-dev-myfoundryname.cognitiveservices.azure.com/`
   - **Key**: Found under "Models + endpoints" section

## Step 3: Copy this repository

1. Navigate to https://github.com/glsauto/ai-workshop-2025-simple.git
2. Click on "Use this template"
3. Pick a new repository name
4. Click create repository
5. Open a terminal or command prompt
6. Navigate to your desired directory
7. Clone the repository you just created:
   ```
   git clone https://github.com/glsauto/my-repository-name.git
   ```
8. Open the folder in VS Code
9. Copy the sample.env file into a new .env file
10. Update the .env file with your endpoint and api key


## Step 4: Install Python dependencies and Launch the app

```
pip install -r requirements.txt
python app.py
```

## Troubleshooting Tips

1. **Authentication Error**: Double-check your API key and endpoint URL
2. **Model Not Found**: Ensure you're using the exact deployment name
3. **Rate Limiting**: Check your pricing tier limits

## Next Steps

### Beginner Explorations

- Explore other people's AI Apps!  Peruse https://theresanaiforthat.com/
- Explore the [Azure Foundry Playground](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-playground) for inspiration.  
- Try multi-modal. Update the example repo and ask the LLM to [describe an image](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/gpt-with-vision?tabs=rest). 
- Explore randomness. Update the example repo and adjust temperature to make responses more or less random. 

### Intermediate Projects

Explore tool calling.   Tools allow your chatbot to use your python code, example [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/function-calling).  Most AI agents are [simply an LLM in a loop with tools](https://sketch.dev/blog/agent-loop)!  You can peek behind the curtain and study how the big players reference tools in their system prompts, [here](https://github.com/elder-plinius/CL4R1T4S/tree/main). 

Create a frontend. Use an AI coding assistant to create an html/js frontend to call this app.

Upgrade the python app to an api. Add Flask or FastAPI to the project. Alternatively, make the backend an Azure Function.

Create a simple RAG app. Get data from a website, api, or database, and then inject it into the prompt!  Pairs nicely with tool calling!  

### Advanced Challenges

Have the LLM use our data.  Ingest GLS data into Azure AI Search index, then use it as a data source during conversations.  Try it in the Azure Foundry playground [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/use-your-data-quickstart?tabs=keyless%2Ctypescript-keyless%2Cpython-new&pivots=ai-foundry-portal). Python code examples [here](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/references/on-your-data?tabs=python#examples).

Add a voice! Create a realtime voice agent. See [GPT-4o Realtime API for speech and audio (Preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/realtime-audio-quickstart?tabs=api-key%2Cwindows&pivots=programming-language-python).  Explore Voice + RAG proof-of-concept.  It is deployed [here](https://ai.dev.glsauto.com/), and codebase is [here](https://github.com/glsauto/acs-realtime-voice-agent). 






