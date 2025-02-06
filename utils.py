import typesense
from dotenv import load_dotenv
import os

load_dotenv()
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")


class Typesense:
    def __init__(self, nodes: list, api_key: str):
        self.nodes = nodes
        self.api_key = api_key
        self.client = typesense.Client(
            {
                "nodes": nodes,
                "api_key": api_key,
                # 'connection_timeout_seconds': 2
            }
        )
    
    def create_collection(self, schema, file_path, file_type):
        try:
            self.client.collections.create(schema=schema)
            with open(file_path) as file:
                self.client.collections[schema['name']].documents.import_(file.read().encode('utf-8'))

        except Exception as e:
            return e


# symantic and hybrid search and keyword search

