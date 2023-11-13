import streamlit as st
import pandas as pd
import io
from PIL import Image

# # st.set_page_config(layout="wide")
image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo')

# Upload image
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Define data types and properties
properties = {
    'Kunde': str,
    'Benennung': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Gewicht': float,
    'Material Kosten': float,
    'Brennen': float,
    'Schlossern': float,
    'Schweißen': float,
    'sonstiges (Eur/hour)': float,
    'sonstiges (hour)': float,
    'Prüfen , Doku': float,
    'Strahlen / Streichen': float,
    'techn. Bearb.': float,
    'mech. Vorbearb.': float,
    'mech. Bearbeitung': float,
    'Zwischentransporte': float,
    'transporte': float,
}

units = {
    'Gewicht': 'kg',
    'Material Kosten': '€',
    'Brennen': 'min',
    'Schlossern': 'min',
    'Schweißen': 'min',
    'sonstiges (Eur/hour)': '€/min',
    'sonstiges (hour)': 'min',
    'Prüfen , Doku': '€',
    'Strahlen / Streichen': '€',
    'techn. Bearb.': '€',
    'mech. Vorbearb.': '€',
    'mech. Bearbeitung': '€',
    'Zwischentransporte': '€',
    'transporte': '€',
}

# Initialize session state for each property
if "data" not in st.session_state:
    st.session_state.deckung_data = {prop: "" for prop in properties}

st.title("Deckung")

# cols1 = st.columns([0.3,0.3,0.4])

# Project Details Expander
with st.expander("Project Details"):
    for prop in ['Kunde', 'Benennung', 'Zeichnungs- Nr.', 'Ausführen Nr.']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()

# Product Details Expander
with st.expander("Product Details"):
    for prop in ['Gewicht', 'Material Kosten']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        if properties[prop] == float:
            current_value = float(st.session_state.deckung_data[prop]) if st.session_state.deckung_data[prop] else 0.0
            st.session_state.deckung_data[prop] = st.number_input(prompt, value=current_value, step=0.1)
        else:
            st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()

with st.expander("Material Cost Details"):
    df = pd.DataFrame(
        index=["0 – 80mm", "80 – 170mm", "Profile, Rohre etc.", "Schrauben, Schild", "Zuschlag", "Total"],
        columns=["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)", "Price per Kg(€/Kg)"]
    )

    if 'Material' in st.session_state:
        df = pd.DataFrame.from_dict(st.session_state['Material']).transpose()
    else:
        st.session_state['Material'] = df.to_dict(orient="index")

    edited_df = st.data_editor(df)

    if st.button('Calculate Totals'):
        # Convert the DataFrame columns to numeric values where possible
        for col in edited_df.columns:
            edited_df[col] = pd.to_numeric(edited_df[col], errors='ignore')

        # Compute the total for each column (excluding "Price per kg") and update the "Total" row values
        edited_df.loc["Total", ["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)"]] = edited_df.loc[
                                                                                               :"Zuschlag",
                                                                                               ["Calculated Weight(Kg)",
                                                                                                "Delivery Weight(Kg)",
                                                                                                "Price(€)"]].sum()
        st.session_state['Material'] = edited_df.to_dict(orient="index")

with st.expander("Deckungsbeitrag"):
    # Initialize session state for Erlös, Deckungsbeitrag, and DB if not already initialized
    if "erlos" not in st.session_state:
        st.session_state.erlos = 0.0
    if "deckungsbeitrag" not in st.session_state:
        st.session_state.deckungsbeitrag = 0.0
    if "db_percentage" not in st.session_state:
        st.session_state.db_percentage = 0.0

    # Input fields
    st.session_state.erlos = st.number_input("Erlös (€)", value=st.session_state.erlos)
    st.session_state.db_percentage = st.number_input("DB (%)", value=st.session_state.db_percentage, step=0.01)
    st.session_state.deckungsbeitrag = st.number_input("Deckungsbeitrag (€)", value=st.session_state.deckungsbeitrag)

# Gesamtstuden expander
with st.expander("Gesamtstuden"):
    for prop in ['Brennen', 'Schlossern', 'Schweißen', 'sonstiges (Eur/hour)', 'sonstiges (hour)']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()

# Grenzkosten expander
with st.expander("Grenzkosten"):
    for prop in ['Prüfen , Doku', 'Strahlen / Streichen', 'techn. Bearb.', 'mech. Vorbearb.', 'mech. Bearbeitung',
                 'Zwischentransporte', 'transporte']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()
#
# Convert the user input data dictionary to a pandas DataFrame
# df = pd.DataFrame([st.session_state.data])
# Combine data for downloads
combined_data = {
    **st.session_state.data,
    **st.session_state.deckung_data,# Project and Product Details
    **st.session_state['Material'],  # Material Cost Details
    'Erlös': st.session_state.erlos,
    'DB (%)': st.session_state.db_percentage,
    'Deckungsbeitrag': st.session_state.deckungsbeitrag,
}

# Convert the combined data to a pandas DataFrame
df = pd.DataFrame([combined_data])

# Add a button to download the data as Excel
if st.button("Download as Excel"):
    # Convert relevant values to numeric types
    hourly_rate = pd.to_numeric(st.session_state.data['sonstiges (Eur/hour)'], errors='coerce')
    hours = pd.to_numeric(st.session_state.data['sonstiges (hour)'], errors='coerce')
    # Create a dictionary with the data
    data_dict = {
        'Kunde': st.session_state.data['Kunde'],
        'Benennung': st.session_state.data['Benennung'],
        'Anfr. Nr.': st.session_state.data['Zeichnungs- Nr.'],
        'Gewicht': st.session_state.data['Gewicht'],
        'Material': st.session_state.data['Material Kosten'],
        'Brennen': st.session_state.data['Brennen'],
        'Schlossern': st.session_state.data['Schlossern'],
        'Schweißen': st.session_state.data['Schweißen'],
        'sonstiges': hourly_rate * hours,
        'Gesamtstunden': (
                st.session_state.data['Brennen'] +
                st.session_state.data['Schlossern'] +
                st.session_state.data['Schweißen'] +
                st.session_state.data['sonstiges (hour)'] +
                st.session_state.data['sonstiges (Eur/hour)']
        ),
        'Stunden / Tonne': 0 if st.session_state.data['Gewicht'] == 0 else st.session_state.data['Gesamtstunden'] /
                                                                           st.session_state.data['Gewicht'],
        'Fertigung EUR': (
                st.session_state.data['Brennen'] +
                st.session_state.data['Schlossern'] +
                st.session_state.data['Schweißen'] +
                st.session_state.data['sonstiges (hour)'] +
                st.session_state.data['sonstiges (Eur/hour)']
        ),
        'Glühen': 0,  # You need to replace this with the actual value for 'Glühen'
        'Prüfen , Doku': st.session_state.data['Prüfen , Doku'],
        'Strahlen / Streichen': st.session_state.data['Strahlen / Streichen'],
        'techn. Bearb.': st.session_state.data['techn. Bearb.'],
        'mech. Vorbearb.': st.session_state.data['mech. Vorbearb.'],
        'mech. Bearbeitung': st.session_state.data['mech. Bearbeitung'],
        'Zwischentransporte': st.session_state.data['Zwischentransporte'],
        'Transporte': st.session_state.data['transporte'],
        'Grenzkosten': (
                st.session_state.data['Prüfen , Doku'] +
                st.session_state.data['Strahlen / Streichen'] +
                st.session_state.data['techn. Bearb.'] +
                st.session_state.data['mech. Vorbearb.'] +
                st.session_state.data['mech. Bearbeitung'] +
                st.session_state.data['Zwischentransporte'] +
                st.session_state.data['transporte']
        ),
        'Erlös': st.session_state.erlos,
        'DB': st.session_state.deckungsbeitrag,
        'Soll 10%': st.session_state.erlos * 0.1,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag
    }

    # Convert the dictionary to a DataFrame
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame([data_dict])

    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.T.to_excel(writer, sheet_name='user_data', header=False)
    excel_file.seek(0)

    # Download the Excel file using st.download_button
    st.download_button(label="Click here to download the Excel file", key="download_excel", data=excel_file,
                       file_name="user_data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Add a button to download the data as JSON
if st.button("Download as JSON"):
    # Convert the DataFrame to JSON
    json_data = df.to_json(orient="records")

    # Download the JSON file using st.download_button
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")
