import typesense
import wave
import base64
import requests

client = typesense.Client({
  'nodes': [{
    'host': 'localhost', # For Typesense Cloud use xxx.a1.typesense.net
    'port': '8108',      # For Typesense Cloud use 443
    'protocol': 'http'   # For Typesense Cloud use https
  }],
  'api_key': 'QL84oZvREWNAm8zKEUWmeBe43xDF3uOQRazWeqIDrGw9cucZ',
  # 'connection_timeout_seconds': 2
})

books_schema = {
  'name': 'books',
  'fields': [
    {'name': 'title', 'type': 'string' },
    {'name': 'authors', 'type': 'string[]', 'facet': True },
    {'name': 'publication_year', 'type': 'int32', 'facet': True },
    {'name': 'ratings_count', 'type': 'int32' },
    {'name': 'average_rating', 'type': 'float' }
  ],
  'default_sorting_field': 'ratings_count',
  "voice_query_model": {
        "model_name": "ts/whisper/base.en"
    }
}




# client.collections["books"].delete()
# client.collections.create(books_schema)


with open('books.jsonl') as jsonl_file:
  client.collections['books'].documents.import_(jsonl_file.read().encode('utf-8'))


voice_query_file = open('voice_query1.wav', 'rb')
voice_query_data = base64.b64encode(voice_query_file.read()).decode('utf-8')


search_parameters = {
  'q' : 'carry sotter',
  'query_by'  : 'title',
  'sort_by'   : 'ratings_count:desc'
}

search_parameters = {
  'q' : voice_query_data,
  'query_by'  : 'title',
  'sort_by'   : 'ratings_count:desc'
}

# d = dict(client.collections['books'].documents.search(search_parameters))

# documents = d["hits"]
# for i in documents:
#   for j in i["highlights"]:
#     print(j["snippet"])
#     print("\n")

TYPESENSE_API_KEY = "your_api_key"
TYPESENSE_HOST = "http://localhost:8108/multi_search"  # Default port for Typesense

headers = {"X-TYPESENSE-API-KEY": "QL84oZvREWNAm8zKEUWmeBe43xDF3uOQRazWeqIDrGw9cucZ"}

response = requests.post(TYPESENSE_HOST, json=search_parameters, headers=headers)

print(response)
