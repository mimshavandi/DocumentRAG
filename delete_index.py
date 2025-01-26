# delete_index.py

from azure_vector_helper import AzureSearchRESTHelper

def delete_existing_index():
    try:
        index_helper = AzureSearchRESTHelper(env_file="local.env", index_definition_file="index_definition.json")
        index_helper.delete_index()
    except Exception as e:
        print(f"Error deleting index: {e}")

if __name__ == "__main__":
    delete_existing_index()
