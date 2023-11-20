import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os

# Initialize Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


# Function to get all collection names from Firestore database
def get_all_collections(db):
    excluded_collections = {'operators', 'posts', 'projects'}  # Set of collections to exclude
    collections = db.collections()
    return [collection.id for collection in collections if collection.id not in excluded_collections]


# Function to get all document IDs from a Firestore collection
def get_all_document_ids(collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.id for doc in docs]


# Function to get data from Firestore for a specific document in a collection
def get_data_from_firestore(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None


# Function to upload data to Firestore
def upload_data_to_firestore(db, collection_name, document_id, data):
    doc_ref = db.collection(collection_name).document(document_id)
    doc_ref.set(data)
    st.success("Data uploaded successfully!")


image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Define data types and properties
properties = {
    'Kunde': str,
    'Gegenstand': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Brennen': float,
    'Richten': float,
    'Heften_Zussamenb_Verputzen': float,
    'Anzeichnen': float,
    'Schweißen': float,
}

units = {
    'Brennen': 'min',
    'Richten': 'min',
    'Heften_Zussamenb_Verputzen': 'min',
    'Anzeichnen': 'min',
    'Schweißen': 'min',
}

firestore_data = {}

# Display a select box with all collection names
collection_names = get_all_collections(db)
selected_collection = st.selectbox('Select Collection:', options=collection_names)

# Initialize session state for each property
if "vk_0_data" not in st.session_state:
    st.session_state.vk_0_data = {prop: "" for prop in properties}

# Fetch and display the data for a known document ID ('Details') from the selected collection
if selected_collection:
    firestore_data = get_data_from_firestore(selected_collection, 'Details')

# Update the session state data for specific fields when a new collection is selected
if st.session_state.vk_0_data and selected_collection:
    for prop in st.session_state.vk_0_data.keys():
        if prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']:
            st.session_state.vk_0_data[prop] = ""

col1, col2 = st.columns(2)

props_col1 = list(properties.keys())[:len(properties) // 2]
props_col2 = list(properties.keys())[len(properties) // 2:]

for prop in props_col1:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_0_data[prop] = col1.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()

for prop in props_col2:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.vk_0_data[prop] = col2.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()

# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame(st.session_state.vk_0_data, index=[0])  # Specify index to create a DataFrame with one row

# Transpose the DataFrame to have each column stacked vertically
df_transposed = df.transpose()

# Download Excel and JSON
if st.button("Download Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_transposed.to_excel(writer, sheet_name='Sheet1', header=False)  # Set header to False to exclude column names
    output.seek(0)
    st.download_button("Download Excel File", output, key="download_excel", file_name="data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.button("Download JSON"):
    json_data = df.to_json(orient="records")
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

if st.button("Upload to Database"):
    # Convert session state data to the appropriate format for Firestore
    # Assuming your Firestore expects a dictionary with specific keys
    upload_data = {field_mapping.get(k, k): v for k, v in st.session_state.vk_0_data.items()}
    upload_data_to_firestore(db, selected_collection, 'VK-0', upload_data)
