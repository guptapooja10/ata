import streamlit as st
import pandas as pd
import io
#from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import streamlit_antd_components as sac
import os

sac.segmented(

        items=[
            sac.SegmentedItem(label='Schweißen', href='https://ata-vk-0.streamlit.app/'),
            sac.SegmentedItem(label='About', href='https://aboutpage.streamlit.app/'),
            sac.SegmentedItem(label='Sign In', href='https://credentials-page.streamlit.app/'),
            sac.SegmentedItem(label='Project Instantiation', href='https://ata-app-navigator.streamlit.app/'),
            sac.SegmentedItem(label='Material List', href='https://vk-st-0.streamlit.app/'),
            sac.SegmentedItem(label='Deckung', href='https://deckung.streamlit.app/'),
            sac.SegmentedItem(label='Angebot', href='https://angebot.streamlit.app/'),
            sac.SegmentedItem(label='Project Status', href='https://ata-project-status.streamlit.app/'), ],
        align='end', size='sm', bg_color='transparent'
    )


# navigation_bar()

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


def get_data_from_firestore(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None


def upload_data_to_firestore(db, collection_name, document_id, data):
    doc_ref = db.collection(collection_name).document(document_id)
    doc_ref.set(data)
    st.success("Data uploaded successfully!")


#image = Image.open('logo_ata.png')
#st.image(image, caption='Ata Logo', use_column_width=True)

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

field_mapping = {
    'Kunde': 'Kunde',
    'Gegenstand': 'Benennung',  # Note the different field name here
    'Zeichnungs- Nr.': 'Zeichnungs- Nr.',
    'Ausführen Nr.': 'Ausführen Nr.'
}

# Initialize session state for each property
if "vk_0_data" not in st.session_state:
    st.session_state.vk_0_data = {prop: "" for prop in properties}
# Define a key in session state to track the currently selected collection
if 'current_collection' not in st.session_state:
    st.session_state.current_collection = None
# Display a select box with all collection names
collection_names = get_all_collections(db)
# Update session state with selected collection
selected_collection = st.selectbox('Select Collection:', options=collection_names)
firestore_data = {}
details_data = {}
vk_0_data = {}

# Check if the selected collection has changed
if st.session_state.current_collection != selected_collection:
    st.session_state.current_collection = selected_collection

    # Clear the previous data from session state
    st.session_state.vk_0_data = {prop: "" for prop in properties}

    # Load new data from Firestore for the selected collection
    if selected_collection:
        firestore_data = get_data_from_firestore(selected_collection, 'Details')
        vk_0_data = get_data_from_firestore(selected_collection, 'VK-0')

        # Update session state with new data
        if firestore_data:
            for app_field, firestore_field in field_mapping.items():
                st.session_state.vk_0_data[app_field] = firestore_data.get(firestore_field, "")

# Update session state with data from 'Details'
if details_data:
    for app_field, firestore_field in field_mapping.items():
        if app_field in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']:  # Fields from 'Details'
            st.session_state.data[app_field] = details_data.get(firestore_field, "")

# Update session state with data from 'VK-0'
if vk_0_data:
    for prop in properties:
        if prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']:  # Remaining fields
            st.session_state.vk_0_data[prop] = vk_0_data.get(prop, "")

st.title("Schweißen")

# If firestore_data is fetched, update the session state
if firestore_data:
    for app_field, firestore_field in field_mapping.items():
        # Assuming 'Gegenstand' should map to 'Benennung' in Firestore
        if app_field == 'Gegenstand':
            firestore_field = 'Benennung'
        st.session_state.vk_0_data[app_field] = firestore_data.get(firestore_field, "")

# col1, col2 = st.columns(2)
#
# props_col1 = list(properties.keys())[:len(properties) // 2]
# props_col2 = list(properties.keys())[len(properties) // 2:]
#
# for prop in props_col1:
#     prompt = f"{prop} ({units.get(prop, '')})"
#     # Use the session state data to populate the fields
#     st.session_state.vk_0_data[prop] = col1.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()
#
# for prop in props_col2:
#     prompt = f"{prop} ({units.get(prop, '')})"
#     # Use the session state data to populate the fields
#     st.session_state.vk_0_data[prop] = col2.text_input(prompt, value=st.session_state.vk_0_data[prop]).strip()

# Define the expanders
with st.expander("Customer"):
    # Input fields for customer-related data
    st.text_input("Kunde", value=st.session_state.vk_0_data["Kunde"])
    st.text_input("Gegenstand", value=st.session_state.vk_0_data["Gegenstand"])
    st.text_input("Zeichnungs- Nr.", value=st.session_state.vk_0_data["Zeichnungs- Nr."])
    st.text_input("Ausführen Nr.", value=st.session_state.vk_0_data["Ausführen Nr."])

with st.expander("Processing Times"):
    # Input fields for processing times
    st.number_input("Brennen (min)", value=float(st.session_state.vk_0_data["Brennen"]))
    st.number_input("Richten (min)", value=float(st.session_state.vk_0_data["Richten"]))
    st.number_input("Heften_Zussamenb_Verputzen (min)", value=float(st.session_state.vk_0_data["Heften_Zussamenb_Verputzen"]))
    st.number_input("Anzeichnen (min)", value=float(st.session_state.vk_0_data["Anzeichnen"]))
    st.number_input("Schweißen (min)", value=float(st.session_state.vk_0_data["Schweißen"]))


def perform_calculations(data):
    # Convert relevant fields to numeric type
    numeric_fields = ['Brennen', 'Richten', 'Heften_Zussamenb_Verputzen', 'Anzeichnen', 'Schweißen']
    for field in numeric_fields:
        data[field] = float(data[field]) if data[field] else 0.0

    # Perform the specified calculations
    data['Brennen_VK_0'] = data['Brennen'] / 60
    data['Schlossern_VK_0'] = (data['Richten'] + data['Heften_Zussamenb_Verputzen'] + data['Anzeichnen']) / 60
    data['Schweißen_VK_0'] = data['Schweißen'] / 60
    return data


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
    # Extract the user input data
    user_input_data = {prop: st.session_state.vk_0_data[prop] for prop in properties if
                       prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']}

    # Perform calculations on the input data
    user_input_data_calculated = perform_calculations(user_input_data)

    # Upload the original and calculated data to the database
    upload_data_to_firestore(db, selected_collection, 'VK-0', user_input_data_calculated)

    st.success("Data uploaded successfully!")
