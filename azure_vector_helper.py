# azure_search_rest_helper.py

import requests
import os
import json
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    filename='RAG/azure_search_rest_helper.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class AzureSearchRESTHelper:
    def __init__(self, env_file: str = "local.env", index_definition_file: str = "index_definition.json"):
        """
        Initializes the AzureSearchRESTHelper by loading environment variables and the index definition.

        :param env_file: Path to the environment variables file.
        :param index_definition_file: Path to the index definition JSON file.
        """
        load_dotenv(dotenv_path=env_file)
        
        self.endpoint = os.getenv("ACS_ENDPOINT")
        self.api_key = os.getenv("ACS_API_KEY")
        self.index_name = os.getenv("ACS_INDEX_NAME", "knowledge-index")
        self.api_version = "2024-07-01"  # Ensure this matches your target API version
        self.index_definition_file = index_definition_file
        
        if not all([self.endpoint, self.api_key]):
            error_msg = "Azure Cognitive Search configuration is incomplete. Please check your local.env file."
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        # Read the index definition from the JSON file
        try:
            with open(self.index_definition_file, "r", encoding="utf-8") as f:
                self.index_definition = json.load(f)
            logging.info(f"Loaded index definition from '{self.index_definition_file}'.")
        except FileNotFoundError:
            error_msg = f"Index definition file '{self.index_definition_file}' not found."
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Error decoding JSON from '{self.index_definition_file}': {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)
    
    def create_or_update_index(self):
        """
        Creates or updates an Azure Cognitive Search index using the REST API.

        :return: None
        """
        url = f"{self.endpoint}/indexes/{self.index_name}?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        response = requests.put(url, headers=headers, json=self.index_definition)
        
        if response.status_code in [200, 201]:
            logging.info(f"Index '{self.index_name}' created/updated successfully.")
            print(f"Index '{self.index_name}' created/updated successfully.")
        else:
            try:
                error_message = response.json().get("error", {}).get("message", response.text)
            except json.JSONDecodeError:
                error_message = response.text
            logging.error(f"Failed to create/update index '{self.index_name}': {error_message}")
            raise Exception(f"Failed to create/update index '{self.index_name}': {error_message}")
    
    def delete_index(self):
        """
        Deletes an Azure Cognitive Search index using the REST API.

        :return: None
        """
        url = f"{self.endpoint}/indexes/{self.index_name}?api-version={self.api_version}"
        headers = {
            "api-key": self.api_key
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:
            logging.info(f"Index '{self.index_name}' deleted successfully.")
            print(f"Index '{self.index_name}' deleted successfully.")
        elif response.status_code == 404:
            logging.warning(f"Index '{self.index_name}' does not exist.")
            print(f"Index '{self.index_name}' does not exist.")
        else:
            try:
                error_message = response.json().get("error", {}).get("message", response.text)
            except json.JSONDecodeError:
                error_message = response.text
            logging.error(f"Failed to delete index '{self.index_name}': {error_message}")
            raise Exception(f"Failed to delete index '{self.index_name}': {error_message}")
