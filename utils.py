import typesense
from dotenv import load_dotenv
import os


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
    
