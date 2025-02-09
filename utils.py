import typesense
import pandas as pd
import json
import base64
import requests


class Typesense:
    def __init__(self, nodes: list, api_key: str):
        """
        Initialize the Typesense client.

        Args:
            nodes (list): A list of nodes for the Typesense cluster.
            api_key (str): The API key for accessing the Typesense cluster.
        """
        self.nodes = nodes
        self.api_key = api_key
        self.client = typesense.Client(
            {
                "nodes": nodes,
                "api_key": api_key,
            }
        )

    def create_collection(self, schema: dict):
        """
        Create a collection in Typesense.

        Args:
            schema (dict): The schema of the collection to be created.

        Returns:
            str: A message indicating whether the collection was created or already exists.
        """
        try:
            self.client.collections.create(schema=schema)
            return "Collection created!"
        except Exception as e:
            return e

    def get_collection_names(self):
        """
        Retrieve the names of all collections in Typesense.

        Returns:
            list: A list of collection names.
        """
        collection_names = [col["name"] for col in self.client.collections.retrieve()]
        return collection_names

    def import_documents_into_collection(
        self, collection_name: str, uploaded_file, file_type: str
    ):
        """
        Import documents into a specified collection.

        Args:
            collection_name (str): The name of the collection to import documents into.
            uploaded_file: The file containing the documents to be imported.
            file_type (str): The type of the file ('json', 'jsonl', 'csv', 'xlsx').

        Raises:
            Exception: If there is an error during the import process.
        """
        try:
            if file_type == "json":
                documents = json.load(uploaded_file)
            elif file_type == "jsonl":
                documents = uploaded_file.read().decode("utf-8")
            elif file_type == "csv":
                df = pd.read_csv(uploaded_file)
                documents = df.to_dict(orient="records")
            elif file_type == "xlsx":
                df = pd.read_excel(uploaded_file)
                documents = df.to_dict(orient="records")
            self.client.collections[collection_name].documents.import_(documents)

        except Exception as e:
            raise e

    def search_typed_query(
        self,
        collection_name: str,
        query: str,
        query_by: str,
        sort_by: str,
        sort_order: str,
    ):
        """
        Search for documents in a collection using a typed query.

        Args:
            collection_name (str): The name of the collection to search in.
            query (str): The search query.
            query_by (str): The fields to query by.
            sort_by (str): The field to sort by.
            sort_order (str, optional): The order to sort by ('asc' or 'desc'). Defaults to None.

        Returns:
            df (Dataframe): All the hits fetched from the search.
            found (str): Number of items found message.
            time_taken (str): Time taken in ms message.
        """
        search_parameters = {
            "q": query,
            "query_by": query_by,
            "sort_by": f"{sort_by}:{sort_order}",
            "per_page": 250,
            "page": 1,
        }

        result = dict(
            self.client.collections[collection_name].documents.search(search_parameters)
        )

        hits = [hit["document"] for hit in result["hits"]]
        while True:
            if int(result["found"]) > len(hits):
                search_parameters["page"] += 1
                result = dict(
                    self.client.collections[collection_name].documents.search(
                        search_parameters
                    )
                )
                hits.extend([hit["document"] for hit in result["hits"]])
            else:
                break

        found = result["found"]
        out_of = result["out_of"]
        time_taken = result["search_time_ms"]
        df = pd.DataFrame(hits)
        return df, found, out_of, time_taken

    def search_voice_query(
        self,
        collection_name: str,
        audio_data,
        query_by: str,
        sort_by: str,
        sort_order: str,
    ):
        """
        Search for documents in a collection using a voice query.

        Args:
            collection_name (str): The name of the collection to search in.
            audio_data: The audio data to be used as the search query.
            query_by (str): The fields to query by.
            sort_by (str): The field to sort by.
            sort_order (str, optional): The order to sort by ('asc' or 'desc'). Defaults to None.

        Returns:
            dict: The search results.
        """
        search_parameters = {
            "searches": [
                {
                    "collection": collection_name,
                    "query_by": query_by,
                    "voice_query": audio_data,
                    "sort_by": f"{sort_by}:{sort_order}",
                    "per_page": 250,
                    "page": 1,
                }
            ]
        }

        TYPESENSE_HOST = "http://localhost:8108/multi_search"
        headers = {"X-TYPESENSE-API-KEY": self.api_key}
        response = requests.post(
            TYPESENSE_HOST, json=search_parameters, headers=headers
        )

        return response.json()
