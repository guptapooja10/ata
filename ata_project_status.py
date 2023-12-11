import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)


# Navigation bar
def navigation_bar():
    apps = {
        "Login page": "https://credentials-page.streamlit.app/",
        "Project Instantiation": "https://ata-app-navigator.streamlit.app/",
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",

    }

    st.sidebar.title('Navigation')

    for app_name, app_url in apps.items():
        st.sidebar.markdown(f"[{app_name}]({app_url})")


key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


def get_all_collections(db):
    excluded_collections = {'operators', 'posts', 'projects'}
    collections = db.collections()
    return [collection.id for collection in collections if collection.id not in excluded_collections]


def get_all_document_ids(collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.id for doc in docs]


# Function to get total number of fields in a document
def get_total_fields(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    document = doc_ref.get()

    def count_fields(data):
        total_fields = 0
        for key, value in data.items():
            total_fields += 1
            if isinstance(value, dict):
                total_fields += count_fields(value)
        return total_fields

    if document.exists:
        return count_fields(document.to_dict())
    else:
        return 0


def get_populated_fields_count(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    document = doc_ref.get()

    def count_populated_fields(data):
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += count_populated_fields(value)
            elif value is not None:
                count += 1
        return count

    if document.exists:
        return count_populated_fields(document.to_dict())
    else:
        return 0


# Kunde details
def get_kunde_from_details(document_id):
    details_ref = db.collection("Details").document(document_id)
    details_data = details_ref.get().to_dict()
    kunde_value = details_data.get("Kunde")
    return kunde_value


# Function to get total and populated fields for each document
def get_fields_information(collection_name, document_ids):
    fields_info = []

    for doc_id in document_ids:
        total_fields = get_total_fields(collection_name, doc_id)
        populated_fields_count = get_populated_fields_count(collection_name, doc_id)

        fields_info.append({
            "Document ID": doc_id,
            "Total Fields": total_fields,
            "Populated Fields": populated_fields_count
        })

    return fields_info


# Streamlit app
def main():
    st.title('Project Status App')

    # Display the navigation bar
    navigation_bar()

    # Get all collection IDs
    all_collections = get_all_collections(db)

    # Allow the user to select a collection using a dropdown
    selected_collection = st.selectbox('Select Collection:', all_collections)

    # Get all document IDs for the selected collection
    document_ids = get_all_document_ids(selected_collection)

    # Display 'Kunde' field from the "Details" document in the selected collection
    st.header(f"Kunde Field in Details Document for the Selected Collection: {selected_collection}")
    kunde_value = get_kunde_from_details(selected_collection)
    st.write(f"Kunde: {kunde_value}")

    # Display total and populated fields for each document in the selected collection
    st.header(f"Fields Information for Documents in {selected_collection} Collection:")
    fields_info = get_fields_information(selected_collection, document_ids)

    for info in fields_info:
        st.subheader(f"Document ID: {info['Document ID']}")
        st.write(f"Total Fields: {info['Total Fields']} fields")
        st.write(f"Populated Fields: {info['Populated Fields']} fields")
        st.write('-' * 50)  # Separator for better readability


if __name__ == '__main__':
    main()
