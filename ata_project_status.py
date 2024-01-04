import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os
import matplotlib.pyplot as plt

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)


def fetch_customers(db):
    customers_list = []
    # Assuming you have a collection named 'customers'
    customer_docs = db.collection('Customers').stream()
    for doc in customer_docs:
        # The customer name is the document ID in this case
        customers_list.append(doc.id)
    return customers_list


def fetch_projects_for_customers(db, selected_customers):
    projects = []
    for customer_id in selected_customers:
        customer_ref = db.collection('Customers').document(customer_id)
        customer_doc = customer_ref.get()
        if customer_doc.exists:
            customer_data = customer_doc.to_dict()
            project_list = customer_data.get('Project_List', [])
            projects.extend(project_list)  # Add the projects of this customer to the list
    return projects


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
def get_kunde_from_details(collection_name):
    details_ref = db.collection(collection_name).document("Details")
    details_doc = details_ref.get()

    if details_doc.exists:
        details_data = details_doc.to_dict()
        kunde_value = details_data.get("Kunde")
        return kunde_value
    else:
        st.warning(f"No 'Details' document found in the '{collection_name}' collection.")
        return None


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

    # Fetch and display customer selection
    all_customers = fetch_customers(db)
    selected_customers = st.multiselect('Select Customer:', all_customers)

    # Determine collections to display based on selected customers
    if selected_customers:
        # Fetch projects for selected customers
        collections_to_display = fetch_projects_for_customers(db, selected_customers)
    else:
        # If no customers are selected, display all collections
        collections_to_display = get_all_collections(db)

    # Get all collection IDs
    # all_collections = get_all_collections(db)

    # Allow the user to select a collection using a dropdown
    # selected_collection = st.selectbox('Select Collection:', all_collections)
    selected_collection = st.selectbox('Select Project:', collections_to_display)

    # Get all document IDs for the selected collection
    document_ids = get_all_document_ids(selected_collection)

    # Display 'Kunde' field from the "Details" document in the selected collection
    # st.header(f"Kunde for: {selected_collection}")
    kunde_value = get_kunde_from_details(selected_collection)
    st.write(f"Kunde: {kunde_value}")

    # Display total and populated fields for each document in the selected collection
    # st.header(f"Fields Information for Documents in {selected_collection} Collection:")
    fields_info = get_fields_information(selected_collection, document_ids)

    # Allow the user to select a document ID using a dropdown
    selected_document = st.selectbox('Select Document ID:', document_ids)

    # Find the information for the selected document ID
    selected_info = next((info for info in fields_info if info['Document ID'] == selected_document), None)

    if selected_info:
        st.subheader(f"Document ID: {selected_info['Document ID']}")
        st.write(f"Total Fields: {selected_info['Total Fields']} fields")
        st.write(f"Populated Fields: {selected_info['Populated Fields']} fields")

        # Calculate progress based on the completion of all fields for the selected document
        if selected_info['Total Fields'] > 0:
            remaining_percentage = (selected_info['Total Fields'] - selected_info['Populated Fields']) / selected_info[
                'Total Fields']
            progress = 1.0 - remaining_percentage
            st.progress(progress, f"Progress for Document ID: {selected_info['Document ID']}")
        else:
            st.progress(0.0, f"Progress for Document ID: {selected_info['Document ID']}")
    else:
        st.warning("Please select a valid Document ID.")

        st.write('-' * 50)  # Separator for better readability

    # Calculate total populated fields and delta
    populated_fields_sum = sum(info['Populated Fields'] for info in fields_info)
    total_fields_sum = sum(info['Total Fields'] for info in fields_info)
    delta = total_fields_sum - populated_fields_sum

    # Display progress ratio and total tasks delta in the sidebar
    progress_ratio = populated_fields_sum / total_fields_sum
    # st.sidebar.write(f"Over Progress Ratio: {progress_ratio * 100:.2f}%")
    # st.sidebar.write(f"Total Tasks Delta: {delta}")

    # Display a progress bar for the progress ratio
    st.header("Progress Bar: Over Progress Ratio")
    st.progress(progress_ratio)

    # Display a progress bar for the delta
    st.header("Progress Bar: Total Completed Tasks")
    st.progress(populated_fields_sum)


if __name__ == '__main__':
    main()
