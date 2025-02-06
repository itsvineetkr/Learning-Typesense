import streamlit as st
from dotenv import load_dotenv
import os
from utils import Typesense

load_dotenv()
TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")

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

        # Schema Creation
        st.write("Define Schema")
        schema = []
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

            schema.append({"name": field_name, "type": field_type, "facet": is_facet})

        if st.button("Create Collection"):
            response = ts.create_collection({"name": collection_name, "fields": schema})
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
                df, found, time_taken = results

                st.write("Search Results")
                st.write(f"{found}")
                st.write(f"{time_taken}")
                st.dataframe(df)
            except Exception as e:
                st.error(f"Search Error: {e}")
