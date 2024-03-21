import streamlit as st
import pandas as pd
import io
# from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import streamlit_antd_components as sac
import os

sac.segmented(

    items=[
        sac.SegmentedItem(label='Schweißen', href='https://ata-vk-0.streamlit.app/'),
        # sac.SegmentedItem(label='About', href='https://aboutpage.streamlit.app/'),
        # sac.SegmentedItem(label='Sign In', href='https://credentials-page.streamlit.app/'),
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


# image = Image.open('logo_ata.png')
# st.image(image, caption='Ata Logo', use_column_width=True)

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
    'Schweißnahtnummer': float,
    'Schweißnaht': str,
    'Positionsnummer': str,
    'Lage': str,
    'Nahtlänge': float,
    'Nahtbreite': float,
    'Blechdicke': float,
    'Drahtdurch- messer': float,
    'Masse Drahtelektrode': float,
    'Kosten Drahtelektrode': float,
    'benötigte Drahtrollen': float,
    'Schweißzeit + Nebenzeit': float,
    'Kosten Schweißer': float,
    'Kosten SZ': float,
    'Gesamtkosten': float,
}

units = {
    'Brennen': 'min',
    'Richten': 'min',
    'Heften_Zussamenb_Verputzen': 'min',
    'Anzeichnen': 'min',
    'Schweißen': 'min',
    'Nahtlänge': 'mm',
    'Nahtbreite': 'mm',
    'Blechdicke': 'mm',
    'Drahtdurch- messer': 'mm',
    'Masse Drahtelektrode': 'kg',
    'Kosten Drahtelektrode': '€/kg',
    'Schweißzeit + Nebenzeit': 'h',
    'Kosten Schweißer': '€',
    'Kosten SZ': '€',
    'Gesamtkosten': '€ / Stück',

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
selected_collection = st.sidebar.selectbox('Select Collection:', options=collection_names)
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

dfs = pd.DataFrame(
    [
        {"No.": 1, "Factor1": 7.5, "Factor2": 0},
        {"No.": 2, "Factor1": 12, "Factor2": "MAG 135"},
        {"No.": 3, "Factor1": 20, "Factor2": 2.74},
    ]
)

# Define the expanders
with st.expander("Faktoren Nebenzeiten"):
    edited_df = st.data_editor(dfs, num_rows="dynamic")

with st.expander("Customer"):
    # Input fields for customer-related data
    st.text_input("Kunde", value=st.session_state.vk_0_data["Kunde"])
    st.text_input("Gegenstand", value=st.session_state.vk_0_data["Gegenstand"])
    st.text_input("Zeichnungs- Nr.", value=st.session_state.vk_0_data["Zeichnungs- Nr."])
    st.text_input("Ausführen Nr.", value=st.session_state.vk_0_data["Ausführen Nr."])

with st.expander("Schweißnahtberechnung"):
    # Input fields for processing times
    st.number_input("Brennen (min)", value=float(st.session_state.vk_0_data["Brennen"]))
    st.number_input("Richten (min)", value=float(st.session_state.vk_0_data["Richten"]))
    st.number_input("Heften_Zussamenb_Verputzen (min)",
                    value=float(st.session_state.vk_0_data["Heften_Zussamenb_Verputzen"]))
    st.number_input("Anzeichnen (min)", value=float(st.session_state.vk_0_data["Anzeichnen"]))
    st.number_input("Schweißen (min)", value=float(st.session_state.vk_0_data["Schweißen"]))

weld_names = ["Kehlnaht", "HV 40°", "HV40/15", "HV45°", "HV45°/15", "V 45°", "V60°", "Schrägen"]

with st.expander("Eigenschaften"):
    st.number_input("Schweißnahtnummer",
                    value=float(st.session_state.vk_0_data["Schweißnahtnummer"]) if st.session_state.vk_0_data[
                                                                                        "Schweißnahtnummer"] != "" else 0.0)
    st.selectbox("Schweißnaht", options=weld_names,
                 index=weld_names.index(st.session_state.vk_0_data["Schweißnaht"]) if st.session_state.vk_0_data[
                                                                                          "Schweißnaht"] in weld_names else 0)
    st.text_input("Positionsnummer", value=st.session_state.vk_0_data["Positionsnummer"])
    st.text_input("Lage", value=st.session_state.vk_0_data["Lage"])
    st.number_input("Nahtlänge (mm)",
                    value=float(st.session_state.vk_0_data["Nahtlänge"]) if st.session_state.vk_0_data[
                                                                                "Nahtlänge"] != "" else 0.0)
    st.number_input("Nahtbreite (mm)",
                    value=float(st.session_state.vk_0_data["Nahtbreite"]) if st.session_state.vk_0_data[
                                                                                 "Nahtbreite"] != "" else 0.0)
    st.number_input("Blechdicke (mm)",
                    value=float(st.session_state.vk_0_data["Blechdicke"]) if st.session_state.vk_0_data[
                                                                                 "Blechdicke"] != "" else 0.0)
    st.number_input("Drahtdurch- messer (mm)",
                    value=float(st.session_state.vk_0_data["Drahtdurch- messer"]) if st.session_state.vk_0_data[
                                                                                         "Drahtdurch- messer"] != "" else 0.0)
    masse_drahtelektrode = st.session_state.vk_0_data.get("Masse Drahtelektrode", 0.0)
    kosten_drahtelektrode = st.session_state.vk_0_data.get("Kosten Drahtelektrode", 0.0)
    benotigte_drahtrollen = st.session_state.vk_0_data.get("benötigte Drahtrollen", 0.0)
    schweisszeit_nebenzeit = st.session_state.vk_0_data.get("Schweißzeit + Nebenzeit", 0.0)
    kosten_schweisser = st.session_state.vk_0_data.get("Kosten Schweißer", 0.0)

    # Input fields for Masse Drahtelektrode, Kosten Drahtelektrode, benötigte Drahtrollen, Schweißzeit + Nebenzeit, and Kosten Schweißer
    masse_drahtelektrode_input = st.number_input("Masse Drahtelektrode (kg)", value=float(
        masse_drahtelektrode) if masse_drahtelektrode != "" else 0.0)
    kosten_drahtelektrode_input = st.number_input("Kosten Drahtelektrode (€/kg)", value=float(
        kosten_drahtelektrode) if kosten_drahtelektrode != "" else 0.0)
    benotigte_drahtrollen_input = st.number_input("benötigte Drahtrollen", value=float(
        benotigte_drahtrollen) if benotigte_drahtrollen != "" else 0.0)
    schweisszeit_nebenzeit_input = st.number_input("Schweißzeit + Nebenzeit (h)", value=float(
        schweisszeit_nebenzeit) if schweisszeit_nebenzeit != "" else 0.0)
    kosten_schweisser_input = st.number_input("Kosten Schweißer (€)",
                                              value=float(kosten_schweisser) if kosten_schweisser != "" else 0.0)

    # Calculate Kosten SZ
    kostensz_value = kosten_drahtelektrode_input * benotigte_drahtrollen_input * masse_drahtelektrode_input

    # Store Kosten SZ in session state
    st.session_state.vk_0_data["Kosten SZ"] = kostensz_value

    # Display Kosten SZ
    kosten_sz_input = st.number_input("Kosten SZ (€)", value=kostensz_value)

    # Calculate Gesamtkosten
    gesamtkosten_value = kosten_schweisser_input + kosten_sz_input

    # Store Gesamtkosten in session state
    st.session_state.vk_0_data["Gesamtkosten"] = gesamtkosten_value

    # Display Gesamtkosten
    gesamtkosten_input = st.number_input("Gesamtkosten(€) / Stück", value=gesamtkosten_value)

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
    # Update session state data with values from the input fields inside expanders
    st.session_state.vk_0_data['Brennen'] = st.session_state.vk_0_data['Brennen (min)']
    st.session_state.vk_0_data['Richten'] = st.session_state.vk_0_data['Richten (min)']
    st.session_state.vk_0_data['Heften_Zussamenb_Verputzen'] = st.session_state.vk_0_data['Heften_Zussamenb_Verputzen (min)']
    st.session_state.vk_0_data['Anzeichnen'] = st.session_state.vk_0_data['Anzeichnen (min)']
    st.session_state.vk_0_data['Schweißen'] = st.session_state.vk_0_data['Schweißen (min)']

    # Extract the user input data
    user_input_data = {prop: st.session_state.vk_0_data[prop] for prop in properties if
                       prop not in ['Kunde', 'Gegenstand', 'Zeichnungs- Nr.', 'Ausführen Nr.']}

    # Perform calculations on the input data
    user_input_data_calculated = perform_calculations(user_input_data)

    # Upload the original and calculated data to the database
    upload_data_to_firestore(db, selected_collection, 'VK-0', user_input_data_calculated)

    st.success("Data uploaded successfully!")


