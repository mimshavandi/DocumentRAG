# main.py

import os
import json
from flatten_helper import flatten_submission
from embedding_helper import EmbeddingHelper
from indexing_helper import IndexingHelper
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    filename='RAG/main.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def load_submission(file_path: str) -> dict:
    """
    Load the submission document from a JSON file.

    :param file_path: Path to the JSON file.
    :return: Dictionary representing the submission.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            submission = json.load(f)
        logging.info(f"Loaded submission from '{file_path}'.")
        return submission
    except FileNotFoundError:
        logging.error(f"Submission file '{file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from '{file_path}': {e}")
        raise

def main():
    # Load environment variables
    load_dotenv(dotenv_path="local.env")

    # Configuration
    SUBMISSION_FILE = "RAG/submission.json"  # Path to your submission JSON file

    # Step 1: Load the submission
    try:
        submission = load_submission(SUBMISSION_FILE)
    except Exception as e:
        logging.error(f"Error loading submission: {e}")
        print(f"Error loading submission: {e}")
        return

    # Step 2: Flatten the submission
    try:
        text_summary = flatten_submission(submission)
        logging.info("Flattened Submission:")
        logging.info(text_summary)
        print("Flattened Submission:")
        print(text_summary)
        print("----")
    except Exception as e:
        logging.error(f"Error flattening submission: {e}")
        print(f"Error flattening submission: {e}")
        return

    # Step 3: Initialize and generate embedding
    try:
        embedder = EmbeddingHelper(env_file="local.env")
        embedding_vector = embedder.get_embedding(text_summary)
        logging.info(f"Generated embedding vector of length: {len(embedding_vector)}")
        print(f"Generated embedding vector of length: {len(embedding_vector)}")
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        print(f"Error generating embedding: {e}")
        return

    # Step 4: Initialize Indexing Helper and index the document
    try:
        indexing_helper = IndexingHelper(env_file="local.env")
        doc_id = submission.get("_id")
        user_id = submission.get("user_id")
        folder_id = submission.get("folder_id")
        document_id = submission.get("document_id")
        doc_type = "result"  # Adjust based on your use case (e.g., 'folder', 'document', 'result')

        if not all([doc_id, user_id, folder_id, document_id]):
            logging.error("Missing one or more required fields: '_id', 'user_id', 'folder_id', 'document_id'.")
            print("Missing one or more required fields: '_id', 'user_id', 'folder_id', 'document_id'.")
            raise ValueError("Incomplete submission data.")

        metadata = ""  # Add any additional metadata if needed

        indexing_helper.index_document(
            doc_id=doc_id,
            user_id=user_id,
            folder_id=folder_id,
            document_id=document_id,
            doc_type=doc_type,
            content_text=text_summary,
            embedding_vector=embedding_vector,
            metadata=metadata
        )
        logging.info(f"Successfully indexed document ID: {doc_id}")
        print(f"Successfully indexed document ID: {doc_id}")
    except Exception as e:
        logging.error(f"Error indexing document: {e}")
        print(f"Error indexing document: {e}")
        return

if __name__ == "__main__":
    main()
