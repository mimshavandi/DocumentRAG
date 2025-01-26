import os
import requests
import json
from dotenv import load_dotenv

class IndexingHelper:
    def __init__(self, env_file: str = "local.env"):
        """
        Initializes the IndexingHelper by loading environment variables.
        """
        load_dotenv(dotenv_path=env_file)
        
        self.endpoint = os.getenv("ACS_ENDPOINT")
        self.api_key = os.getenv("ACS_API_KEY")
        self.index_name = os.getenv("ACS_INDEX_NAME")
        self.api_version = "2024-07-01"  # Ensure the correct API version

        if not all([self.endpoint, self.api_key, self.index_name]):
            raise ValueError("Azure Cognitive Search configuration is incomplete. Please check your .env file.")

    def index_document(
        self,
        doc_id: str,
        user_id: str,
        folder_id: str,
        document_id: str,
        doc_type: str,
        content_text: str,
        embedding_vector: list,
        metadata: str = ""
    ) -> None:
        """
        Upserts a single document into Azure Cognitive Search with vector data.

        :param doc_id: Unique identifier for the document.
        :param user_id: ID of the user owning the document.
        :param folder_id: ID of the folder containing the document.
        :param document_id: ID of the document/form.
        :param doc_type: Type of the document (e.g., 'folder', 'document', 'result').
        :param content_text: Flattened text representation of the document.
        :param embedding_vector: Embedding vector as a list of floats.
        :param metadata: Optional metadata as a JSON string or other relevant information.
        """
        url = f"{self.endpoint}/indexes/{self.index_name}/docs/index?api-version={self.api_version}"
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        search_doc = {
            "@search.action": "upload",  # Use 'upload' for adding or replacing documents
            "id": doc_id,
            "userId": user_id,
            "folderId": folder_id,
            "documentId": document_id,
            "type": doc_type,
            "content": content_text,
            "contentVector": embedding_vector,
            "metadata": metadata
        }

        payload = {"value": [search_doc]}

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Successfully indexed document ID: {doc_id}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to index document ID: {doc_id}. Error: {e}")
            raise
