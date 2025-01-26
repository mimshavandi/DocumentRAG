# search_helper.py

import os
import requests
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(
    filename='RAG/search_helper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SearchHelper:
    def __init__(self, env_file: str = "local.env", index_definition_file: str = "index_definition.json"):
        """
        Initializes the SearchHelper by loading environment variables.
        """
        load_dotenv(dotenv_path=env_file)
        self.endpoint = os.getenv("ACS_ENDPOINT")
        self.api_key = os.getenv("ACS_API_KEY")
        self.index_name = os.getenv("ACS_INDEX_NAME", "knowledge-index")
        self.api_version = os.getenv("ACS_API_VERSION", "2024-07-01")
        
        if not all([self.endpoint, self.api_key, self.index_name]):
            error_msg = "Azure Cognitive Search configuration is incomplete. Please check your .env file."
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        logging.info("Initialized SearchHelper.")
    
    def vector_search(self, embedding: list, top_k: int = 5, user_id: str = None) -> dict:
        """
        Performs a vector search against the Azure Cognitive Search index.
        
        :param embedding: The embedding vector to search with.
        :param top_k: Number of top results to return.
        :param user_id: The user ID to filter results. Defaults to None.
        :return: A dictionary containing search results.
        """
        url = f"{self.endpoint}/indexes('{self.index_name}')/docs/search.post.search?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        body = {
            "search": "*",  # Wildcard search to enable vector search alongside other filters
            "vectorQueries": [
                {
                    "kind": "vector",
                    "vector": embedding,
                    "fields": "contentVector",  # Ensure this matches your index's vector field
                    "k": top_k,
                    "exhaustive": False  # Set to True if you need exhaustive search
                }
            ],
            "select": "id, userId, folderId, documentId, type, content, metadata",
            "top": top_k
        }
        
        # Add user filter if user_id is provided
        if user_id:
            body["filter"] = f"userId eq '{user_id}'"
            
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            results = response.json()
            logging.info(f"Vector search successful. Retrieved {len(results.get('value', []))} documents.")
            return results
        except requests.exceptions.HTTPError as http_err:
            try:
                error_message = response.json().get("error", {}).get("message", str(http_err))
            except json.JSONDecodeError:
                error_message = str(http_err)
            logging.error(f"HTTP error during vector search: {error_message}")
            raise Exception(f"HTTP error during vector search: {error_message}")
        except Exception as e:
            logging.error(f"Error during vector search: {e}")
            raise e