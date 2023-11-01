import streamlit as st
import pandas as pd
import io
from PIL import Image

# st.set_page_config(layout="wide")
image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo')

# Define data types and properties
properties = {
    'Kunde': str,
    'Benennung': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Gewicht': float,
    'Material Kosten': float,
}

units = {
    'Gewicht': 'kg',
    'Material Kosten': '€',
}

# Initialize session state for each property
if "data" not in st.session_state:
    st.session_state.data = {prop: "" for prop in properties}

st.title("Deckung")

# cols1 = st.columns([0.3,0.3,0.4])

# Project Details Expander
with st.expander("Project Details"):
    for prop in ['Kunde', 'Benennung', 'Zeichnungs- Nr.', 'Ausführen Nr.']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()

# Product Details Expander
with st.expander("Product Details"):
    for prop in ['Gewicht', 'Material Kosten']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        if properties[prop] == float:
            current_value = float(st.session_state.data[prop]) if st.session_state.data[prop] else 0.0
            st.session_state.data[prop] = st.number_input(prompt, value=current_value, step=0.1)
        else:
            st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()

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

# Convert the user input data dictionary to a pandas DataFrame
# df = pd.DataFrame([st.session_state.data])
# Combine data for downloads
combined_data = {
    **st.session_state.data,  # Project and Product Details
    **st.session_state['Material'],  # Material Cost Details
    'Erlös': st.session_state.erlos,
    'DB (%)': st.session_state.db_percentage,
    'Deckungsbeitrag': st.session_state.deckungsbeitrag,
}

# Convert the combined data to a pandas DataFrame
df = pd.DataFrame([combined_data])


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
