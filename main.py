import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from utils import Typesense

load_dotenv()
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

ts = Typesense(
    nodes=[{"host": "localhost", "port": "8108", "protocol": "http"}],
    api_key=TYPESENSE_API_KEY,
)

st.set_page_config(page_title="Typesense UI", page_icon="🔍", layout="wide")
page = st.sidebar.radio("Navigation", ["Manage Collections", "Search & Sort"])


if page == "Manage Collections":
    st.title("Manage Collections")

    action = st.radio("Choose Action", ["Create Collection", "Delete Collection"])

    if action == "Create Collection":
        st.subheader("Create a New Collection")
        collection_name = st.text_input("Collection Name")

        st.write("Define Schema")
        fields = []
        num_fields = st.number_input("Number of Fields", min_value=1, step=1, value=1)

        for i in range(num_fields):
            col1, col2, col3 = st.columns(3)
            with col1:
                field_name = st.text_input(f"Field {i+1} Name")
            with col2:
                field_type = st.selectbox(
                    f"Field {i+1} Type",
                    ["string", "int32", "float", "bool", "string[]", "auto"],
                )
            with col3:
                is_facet = st.checkbox(f"Facet? {i+1}")

            fields.append({"name": field_name, "type": field_type, "facet": is_facet})

        schema = {
            "name": collection_name,
            "fields": fields,
            "voice_query_model": {"model_name": "ts/whisper/base.en"},
        }

        if st.button("Create Collection"):
            response = ts.create_collection(schema)
            st.success(f"{response}")

        st.write("Upload Data File")
        uploaded_file = st.file_uploader(
            "Upload a CSV, JSONL, XLSX or JSON file",
            type=["csv", "json", "jsonl", "xlsx"],
        )
        file_type = st.selectbox("File Type", ["csv", "json", "jsonl", "xlsx"])

        if uploaded_file and collection_name:
            if st.button("Upload Data"):
                try:
                    ts.import_documents_into_collection(
                        collection_name, uploaded_file, file_type
                    )
                    st.success("Data uploaded successfully!")
                except Exception as e:
                    st.error(f"Upload Error: {e}")

    elif action == "Delete Collection":
        st.subheader("Delete a Collection")
        collections = ts.get_collection_names()
        collection_to_delete = st.selectbox("Select Collection", collections)

        if st.button("Delete Collection"):
            try:
                ts.client.collections[collection_to_delete].delete()
                st.success(f"Collection '{collection_to_delete}' deleted successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

elif page == "Search & Sort":
    st.title("Search & Sort Data")
    collections = ts.get_collection_names()
    collection_name = st.selectbox("Select Collection", collections)

    if collection_name:
        fields = [
            field["name"]
            for field in ts.client.collections[collection_name].retrieve()["fields"]
        ]

        search_field = st.selectbox("Search Field", fields)
        search_query = st.text_input("Search Query")

        sort_field = st.selectbox("Sort By Field", fields)
        sort_order = st.radio("Sort Order", ["asc", "desc"])

        if st.button("Search"):
            try:
                results = ts.search_typed_query(
                    collection_name=collection_name,
                    query=search_query,
                    query_by=search_field,
                    sort_by=sort_field,
                    sort_order=sort_order,
                )
                df, found, out_of, time_taken = results

                st.write("Search Results")

                st.write(
                    f"Took {time_taken} milliseconds for typesense to search query"
                )
                st.write(f"Found {found} result(s) out of {out_of}")

                st.dataframe(df)

            except Exception as e:
                st.error(f"Search Error: {e}")

        st.write(
            "Voice Search: Record a voice message (Working: Using external Whisper from HF)"
        )

        audio_file = st.audio_input("Record audio")
        if audio_file:
            start_time = time.time()
            audio_data = audio_file.read()
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            response = requests.post(
                "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                headers=headers,
                data=audio_data,
            )
            transcript = response.json()["text"]
            end_time = time.time()
            execution_time = end_time - start_time
            try:
                results = ts.search_typed_query(
                    collection_name=collection_name,
                    query=transcript,
                    query_by=search_field,
                    sort_by=sort_field,
                    sort_order=sort_order,
                )
                df, found, out_of, time_taken = results

                st.write("Search Results")

                st.write(
                    f"Took {time_taken} milliseconds for typesense to search query"
                )
                st.write(f"Took {execution_time:.2f} seconds for generating transcript")
                st.write(f"Found {found} result(s) out of {out_of}")

                st.dataframe(df)

            except Exception as e:
                st.error(f"Search Error: {e}")

