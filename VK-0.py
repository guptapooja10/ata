import streamlit as st
import pandas as pd
import io
from PIL import Image
# import xlsxwriter

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Define data types and properties
properties = {
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
    'Brennen': 'Brennen',
    'Richten': 'Richten',
    'Heften_Zussamenb_Verputzen': 'Heften_Zussamenb_Verputzen',
    'Anzeichnen': 'Anzeichnen',
    'Schweißen': 'Schweißen'
}

st.title("Vorkalkulation")

# Initialize session state for each property
if "data" not in st.session_state:
    st.session_state.data = {prop: "" for prop in properties}

col1, col2 = st.columns(2)

props_col1 = list(properties.keys())[:len(properties) // 2]
props_col2 = list(properties.keys())[len(properties) // 2:]

for prop in props_col1:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.data[prop] = col1.text_input(prompt, value=st.session_state.data[prop]).strip()

for prop in props_col2:
    prompt = f"{prop} ({units.get(prop, '')})"
    # Use the session state data to populate the fields
    st.session_state.data[prop] = col2.text_input(prompt, value=st.session_state.data[prop]).strip()

# Convert the user input data dictionary to a pandas DataFrame
df = pd.DataFrame(st.session_state.data, index=[0])  # Specify index to create a DataFrame with one row

# Transpose the DataFrame to have each column stacked vertically
df_transposed = df.transpose()

if st.button("Download Excel"):
    output = io.BytesIO()
    with pd.ExcelWriter(output) as writer:
        df_transposed.to_excel(writer, sheet_name='Sheet1', header=False)  # Set header to False to exclude column names
    output.seek(0)
    st.download_button("Download Excel File", output, key="download_excel", file_name="data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    
if st.button("Download JSON"):
    json_data = df.to_json(orient="records")
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")
