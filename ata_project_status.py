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


def get_kunde_from_details(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id).collection('Details').document('details_doc')
    details_document = doc_ref.get()

    if details_document.exists:
        details_data = details_document.to_dict()
        return details_data.get('Kunde', 'Not available')
    else:
        return 'Details document not found'


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

    # Display 'Kunde' field from the "Details" document for each document in the selected collection
    st.header(f"Kunde Field in Details Document for Documents in {selected_collection} Collection:")
    document_ids = get_all_document_ids(selected_collection)
    for doc_id in document_ids:
        st.write(f"Document ID: {doc_id}")

        kunde_value = get_kunde_from_details(selected_collection, doc_id)
        st.write(f"Kunde: {kunde_value}")
        st.write('-' * 50)  # Separator for better readability

    # Display total number of fields for each document in the selected collection
    st.header(f"Total Number of Fields in Documents of {selected_collection} Collection:")
    for doc_id in document_ids:
        total_fields = get_total_fields(selected_collection, doc_id)
        st.write(f"{doc_id}: {total_fields} fields")
        populated_fields_count = get_populated_fields_count(selected_collection, doc_id)
        st.write(f"{doc_id}: {populated_fields_count} populated fields")




if __name__ == '__main__':
    main()
