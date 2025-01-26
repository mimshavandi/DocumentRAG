# embedding_helper.py

import os
import openai
from dotenv import load_dotenv

class EmbeddingHelper:
    def __init__(self, env_file: str = "local.env"):
        """
        Initializes the EmbeddingHelper by loading environment variables from a specified file.
        
        :param env_file: Path to the environment variables file (default: "local.env")
        """
        load_dotenv(dotenv_path=env_file)
        
        self.api_type = "azure"
        self.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.engine = os.getenv("AZURE_OPENAI_ENGINE", "text-embedding-ada-002")
        
        if not all([self.api_base, self.api_key, self.engine]):
            raise ValueError("Azure OpenAI configuration is incomplete. Please check your local.env file.")
        
        openai.api_type = self.api_type
        openai.api_base = self.api_base
        openai.api_version = self.api_version
        openai.api_key = self.api_key

    def get_embedding(self, text: str) -> list:
        """
        Generate an embedding for the given text using Azure OpenAI.

        :param text: The input text to embed.
        :return: A list of floats representing the embedding vector.
        """
        try:
            response = openai.Embedding.create(
                input=[text],
                engine=self.engine
            )
            embedding = response["data"][0]["embedding"]
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
