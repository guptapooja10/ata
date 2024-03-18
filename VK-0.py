import streamlit as st
import pandas as pd
import io
from google.cloud import firestore
from google.oauth2 import service_account

# Define Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

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
collection_names = db.collection_names()
selected_collection = st.selectbox('Select Collection:', options=collection_names)

# Update session state with selected collection
if st.session_state.current_collection != selected_collection:
    st.session_state.current_collection = selected_collection

    # Clear the previous data from session state
    st.session_state.vk_0_data = {prop: "" for prop in properties}

    # Load new data from Firestore for the selected collection
    if selected_collection:
        firestore_data = db.get_data(selected_collection)
        if firestore_data:
            for app_field, firestore_field in field_mapping.items():
                st.session_state.vk_0_data[app_field] = firestore_data.get(firestore_field, "")

# Define the expanders
with st.expander("Customer"):
    # Input fields for customer-related data
    st.text_input("Kunde", value=st.session_state.vk_0_data["Kunde"])
    st.text_input("Gegenstand", value=st.session_state.vk_0_data["Gegenstand"])
    st.text_input("Zeichnungs- Nr.", value=st.session_state.vk_0_data["Zeichnungs- Nr."])
    st.text_input("Ausführen Nr.", value=st.session_state.vk_0_data["Ausführen Nr."])

with st.expander("Processing Times"):
    # Input fields for processing times
    st.number_input("Brennen (min)", value=st.session_state.vk_0_data["Brennen"])
    st.number_input("Richten (min)", value=st.session_state.vk_0_data["Richten"])
    st.number_input("Heften_Zussamenb_Verputzen (min)", value=st.session_state.vk_0_data["Heften_Zussamenb_Verputzen"])
    st.number_input("Anzeichnen (min)", value=st.session_state.vk_0_data["Anzeichnen"])
    st.number_input("Schweißen (min)", value=st.session_state.vk_0_data["Schweißen"])


# Define functions for data manipulation and upload
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


def upload_data_to_firestore(collection_name, document_id, data):
    db.upload_data(collection_name, document_id, data)
    st.success("Data uploaded successfully!")


# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame(st.session_state.vk_0_data, index=[0])

# Download Excel and JSON
if st.button("Download Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.transpose().to_excel(writer, sheet_name='Sheet1', header=False)
    output.seek(0)
    st.download_button("Download Excel File", output, key="download_excel", file_name="data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.button("Download JSON"):
    json_data = df.to_json(orient="records")
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

if st.button("Upload to Database"):
    # Extract the user input data
    user_input_data = {prop: st.session_state.vk_0_data[prop] for prop in properties}

    # Perform calculations on the input data
    user_input_data_calculated = perform_calculations(user_input_data)

    # Upload the original and calculated data to the database
    upload_data_to_firestore(selected_collection, 'VK-0', user_input_data_calculated)
