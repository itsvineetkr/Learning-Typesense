import typesense
import wave
import base64
import requests

client = typesense.Client(
    {
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "api_key": "QL84oZvREWNAm8zKEUWmeBe43xDF3uOQRazWeqIDrGw9cucZ",
    }
)

# books_schema = {
#   'name': 'books',
#   'fields': [
#     {'name': 'title', 'type': 'string' },
#     {'name': 'authors', 'type': 'string[]', 'facet': True },
#     {'name': 'publication_year', 'type': 'int32', 'facet': True },
#     {'name': 'ratings_count', 'type': 'int32' },
#     {'name': 'average_rating', 'type': 'float' }
#   ],
#   'default_sorting_field': 'ratings_count',
#   "voice_query_model": {
#         "model_name": "ts/whisper/base.en"
#     }
# }

# client.collections["books"].delete()
# client.collections.create(books_schema)
# with open('../example_dataset/books.jsonl') as jsonl_file:
#   client.collections['books'].documents.import_(jsonl_file.read().encode('utf-8'))


voice_query_file = open("output.wav", "rb")
voice_query_data = base64.b64encode(voice_query_file.read()).decode("utf-8")

search_parameters = {
    "searches": [
        {"collection": "books", "query_by": "title", "voice_query": voice_query_data}
    ]
}


TYPESENSE_API_KEY = "your_api_key"
TYPESENSE_HOST = "http://localhost:8108/multi_search"
headers = {"X-TYPESENSE-API-KEY": "QL84oZvREWNAm8zKEUWmeBe43xDF3uOQRazWeqIDrGw9cucZ"}

response = requests.post(TYPESENSE_HOST, json=search_parameters, headers=headers)

print(response.json())