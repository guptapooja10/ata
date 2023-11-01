import streamlit as st
import pandas as pd
import io
from PIL import Image

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Define data types and properties
properties = {
    'Kunde': str,
    'Gegenstand': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Fertigung Gesamt': float,
    'bis 90mm Einsatz': float,
    'bis 90mm Fertig': float,
    'bis 90mm Preis': float,
    'ab 100mm Einsatz': float,
    'ab 100mm Fertig': float,
    'ab 100mm Preis': float,
    'Profile Einsatz': float,
    'Profile fertig': float,
    'Profile Preis': float
}

units = {
    'Fertigung Gesamt': 'kg',
    'bis 90mm Einsatz': 'kg',
    'bis 90mm Fertig': 'kg',
    'bis 90mm Preis': '€',
    'ab 100mm Einsatz': 'kg',
    'ab 100mm Fertig': 'kg',
    'ab 100mm Preis': '€',
    'Profile Einsatz': 'kg',
    'Profile fertig': 'kg',
    'Profile Preis': '€'
}

# Initialize session state for each property
if "data" not in st.session_state:
    st.session_state.data = {prop: "" for prop in properties}

st.title("Material List Data")
col1, col2 = st.columns(2)

props_col1 = list(properties.keys())[:len(properties) // 2]
props_col2 = list(properties.keys())[len(properties) // 2:]

for prop in props_col1:
    prompt = f"{prop}"
    if prop in units:
        prompt += f" ({units[prop]})"
    st.session_state.data[prop] = col1.text_input(prompt, value=st.session_state.data[prop]).strip()

for prop in props_col2:
    prompt = f"{prop}"
    if prop in units:
        prompt += f" ({units[prop]})"
    st.session_state.data[prop] = col2.text_input(prompt, value=st.session_state.data[prop]).strip()

# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame([st.session_state.data])


# Function to download DataFrame as Excel
def download_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    return output.getvalue()


# Function to download DataFrame as JSON
def download_json(df):
    return df.to_json(orient="records")


# Provide download options
if st.button("Download as Excel"):
    excel_data = download_excel(df)
    st.download_button("Download Excel File", excel_data, file_name="data.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.button("Download as JSON"):
    json_data = download_json(df)
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")
