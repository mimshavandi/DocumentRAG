# RAG Implementation with Azure AI Search and Azure OpenAI

This repository demonstrates how to build a Retrieval-Augmented Generation (RAG) chatbot using Azure AI Search for document retrieval and OpenAI's GPT models for generating responses. The chatbot includes:
- **Index setup**
- **Document embedding and indexing**
- **User-specific data filtering**
- **Short-term memory for conversation history**

## Features
- Embeds documents into Azure Cognitive Search for vector search.
- Filters results by user ID to ensure secure and relevant data access.
- Maintains short-term memory of the conversation for context-aware responses.

## Prerequisites
1. Python 3.8 or higher
2. Azure AI Search resource
3. Azure OpenAI resource
4. Install Python dependencies

## Setup
1. Clone the Repository  
2. Set Up Environment Variables  
Create a file named local.env in the root directory with the following content:  
ACS_ENDPOINT=[Your Azure Cognitive Search Endpoint]
ACS_API_KEY=[Your Azure Cognitive Search API Key]  
ACS_INDEX_NAME=knowledge-index  
AZURE_OPENAI_ENDPOINT=[Your Azure OpenAI Endpoint]  
AZURE_OPENAI_API_KEY=[Your Azure OpenAI API Key]   
AZURE_OPENAI_ENGINE=text-embedding-ada-002 (based on what model you deploy in your Azure OpenAI)   
OPENAI_CHAT_MODEL=gpt-4 (based on what model you deploy in your Azure OpenAI)  
CURRENT_USER_ID=userXYZ  
3. Prepare the Index   
Run the setup_index.py script to create or update the Azure Cognitive Search index:   
python setup_index.py   
4. Add Documents   
Prepare your document data in document.json for embedding and indexing. Use the main.py script to process and index the documents:   
python main.py   
5. Ask Questions   
6. Prepare your prompt in the query.txt and use the user_query.py script to query the chatbot:   
python user_query.py   

## File Overview
### azure_vector_helper.py: 
Manages Azure Cognitive Search REST API interactions for creating and updating the index.
### embedding_helper.py: 
Generates embeddings using Azure OpenAI.
### flatten_helper.py: 
Serializes structured documents into plain text for embedding.
### indexing_helper.py: 
Handles adding documents to the Azure Cognitive Search index.
### search_helper.py: 
Retrieves documents using vector search, filtered by user ID.
### main.py: 
Processes and indexes documents.
### user_query.py: 
Manages chatbot interactions and maintains conversation history.
