# main.py

import os
import json
from embedding_helper import EmbeddingHelper
from search_helper import SearchHelper
from dotenv import load_dotenv
import logging
import openai

# Configure logging
logging.basicConfig(
    filename='RAG/user_query.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CONVERSATION_HISTORY_FILE = "RAG/conversation_history.json"  # Path to conversation history file


def load_env(env_file: str = "local.env"):
    """
    Loads environment variables from a .env file.
    """
    load_dotenv(dotenv_path=env_file)
    logging.info("Loaded environment variables.")


def load_conversation_history() -> list:
    """
    Loads conversation history from a JSON file.

    :return: A list of conversation history messages.
    """
    try:
        if os.path.exists(CONVERSATION_HISTORY_FILE):
            with open(CONVERSATION_HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                logging.info(f"Loaded conversation history from '{CONVERSATION_HISTORY_FILE}'.")
                return history
        else:
            logging.info(f"No conversation history file found. Starting fresh.")
            return []
    except Exception as e:
        logging.error(f"Error loading conversation history: {e}")
        return []


def save_conversation_history(history: list) -> None:
    """
    Saves the conversation history to a JSON file.

    :param history: A list of conversation history messages.
    """
    try:
        with open(CONVERSATION_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        logging.info(f"Conversation history saved to '{CONVERSATION_HISTORY_FILE}'.")
    except Exception as e:
        logging.error(f"Error saving conversation history: {e}")


def get_user_query(file_path: str = "RAG/query.txt") -> str:
    """
    Loads the user query from a text file.

    :param file_path: Path to the query text file.
    :return: The user's query as a string.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            query = f.read().strip()
        logging.info(f"User query loaded from '{file_path}': {query}")
        print(query)
        return query
    except FileNotFoundError:
        logging.error(f"Query file '{file_path}' not found.")
        raise FileNotFoundError(f"Query file '{file_path}' not found.")
    except Exception as e:
        logging.error(f"Error reading query from '{file_path}': {e}")
        raise e


def process_results_with_openai_chat(results: list, user_query: str, conversation_history: list) -> str:
    """
    Uses OpenAI's chat model to generate a response based on search results and conversation history.

    :param results: List of documents retrieved from the search.
    :param user_query: The original user query.
    :param conversation_history: List of conversation history messages.
    :return: Generated response as a string.
    """
    try:
        # Add the user query to conversation history
        conversation_history.append({"role": "user", "content": user_query})

        # Include search results as context
        context = "\n\n".join([doc['content'] for doc in results])

        # Build the prompt for Chat Completion
        system_message = (
            "You are an AI assistant that helps answer questions based on provided documents. "
            "Use the information from the documents and the recent conversation history to answer."
        )

        # Add conversation history and context to the messages
        messages = [{"role": "system", "content": system_message}] + conversation_history
        messages.append({"role": "system", "content": f"Documents:\n{context}"})

        response = openai.ChatCompletion.create(
            engine=os.getenv("OPENAI_CHAT_MODEL", "gpt-4"),
            messages=messages,
            max_tokens=250,  # Limit the response to 250 tokens
            temperature=0.5,
            n=1,
            stop=None
        )

        # Extract the answer
        answer = response.choices[0].message['content'].strip()

        # Add the assistant's response to conversation history
        conversation_history.append({"role": "assistant", "content": answer})

        logging.info("Generated response using OpenAI Chat Completion.")
        return answer
    except Exception as e:
        logging.error(f"Error generating response with OpenAI Chat Completion: {e}")
        print(e)
        return "I'm sorry, I couldn't generate a response at this time."


def main():
    # Load environment variables
    load_env()

    # Initialize OpenAI with new endpoint and key
    openai.api_base = os.getenv("OPENAI_API_BASE")
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Initialize helpers
    embedder = EmbeddingHelper()
    searcher = SearchHelper()

    # Load conversation history
    conversation_history = load_conversation_history()

    # Get user query from query.txt
    try:
        user_query = get_user_query()
    except Exception as e:
        print(f"Error loading user query: {e}")
        return

    # Generate embedding
    try:
        embedding = embedder.get_embedding(user_query)
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}")
        print("Error generating embedding. Please try again later.")
        return
    
    # Retrieve the userId from the environment or session
    user_id = os.getenv("CURRENT_USER_ID", "userXYZ")

    # Perform vector search
    try:
        search_results = searcher.vector_search(embedding=embedding, top_k=5, user_id=user_id)
        documents = search_results.get('value', [])
        if not documents:
            print("No relevant documents found.")
            return
    except Exception as e:
        logging.error(f"Vector search failed: {e}")
        print(f"Error performing search: {e}")
        return

    # Display retrieved documents (optional)
    print("\nTop Relevant Documents:")
    for idx, doc in enumerate(documents, start=1):
        print(f"\nDocument {idx}:")
        print(f"ID: {doc['id']}")
        print(f"Type: {doc['type']}")
        print(f"Content: {doc['content']}")
        print(f"Metadata: {doc['metadata']}")

    # Generate response using OpenAI Chat Completion
    try:
        answer = process_results_with_openai_chat(documents, user_query, conversation_history)
        print(f"\nAnswer:\n{answer}")
    except Exception as e:
        logging.error(f"Failed to generate answer with OpenAI Chat Completion: {e}")
        print("Error generating answer. Please try again later.")

    # Save updated conversation history
    save_conversation_history(conversation_history)


if __name__ == "__main__":
    main()
