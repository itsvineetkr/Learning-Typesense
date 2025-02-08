import typesense
import wave
import base64
import requests
import time
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="../.env")

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")

client = typesense.Client(
    {
        "nodes": [{"host": "localhost", "port": "8108", "protocol": "http"}],
        "api_key": TYPESENSE_API_KEY,
    }
)

books_schema = {
    "name": "books",
    "fields": [
        {"name": "title", "type": "string"},
        {"name": "authors", "type": "string[]", "facet": True},
        {"name": "publication_year", "type": "int32", "facet": True},
        {"name": "ratings_count", "type": "int32"},
        {"name": "average_rating", "type": "float"},
    ],
    "default_sorting_field": "ratings_count",
    "voice_query_model": {"model_name": "ts/whisper/base.en"},
}

# client.collections["books"].delete()
# client.collections.create(books_schema)
# with open('/home/vineet/Desktop/Typesense/example_dataset/books.jsonl') as jsonl_file:
#   client.collections['books'].documents.import_(jsonl_file.read().encode('utf-8'))


def using_inbuilt():
    voice_query_file = open("/home/vineet/Desktop/Typesense/testing/example.wav", "rb")
    voice_query_data = base64.b64encode(voice_query_file.read()).decode("utf-8")

    search_parameters = {
        "searches": [
            {
                "collection": "books",
                "query_by": "title",
                "voice_query": voice_query_data,
            }
        ]
    }

    TYPESENSE_API_KEY = "your_api_key"
    TYPESENSE_HOST = "http://localhost:8108/multi_search"
    headers = {"X-TYPESENSE-API-KEY": TYPESENSE_API_KEY}

    response = requests.post(TYPESENSE_HOST, json=search_parameters, headers=headers)
    # print(response.json())


def using_api():
    f = open("/home/vineet/Desktop/Typesense/testing/example.wav", "rb")
    audio_data = f.read()
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(
        "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
        headers=headers,
        data=audio_data,
    )
    transcript = response.json()["text"]

    search_parameters = {
        "q": transcript,
        "query_by": "title",
        "per_page": 250,
        "page": 1,
    }

    result = dict(client.collections["books"].documents.search(search_parameters))
    # print(result)


inbuilt_times = []
api_times = []

for i in range(5):
    start_time = time.time()

    using_inbuilt()

    end_time = time.time()
    execution_time = end_time - start_time
    inbuilt_times.append(float(execution_time))

for i in range(5):
    start_time = time.time()

    using_api()

    end_time = time.time()
    execution_time = end_time - start_time
    api_times.append(float(execution_time))


avg_inbuilt_time = sum(inbuilt_times) / len(inbuilt_times)
avg_api_time = sum(api_times) / len(api_times)

print(f"Average execution time using inbuilt method: {avg_inbuilt_time} seconds")
print(f"Average execution time using API method: {avg_api_time} seconds")
