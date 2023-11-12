import streamlit as st
import pandas as pd
import io
from PIL import Image

# # st.set_page_config(layout="wide")
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
    'sonstiges (Euro/hour)': '€/min',
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


# Gesamtstuden expander
with st.expander("Gesamtstuden"):
    for prop in ['Brennen', 'Schlossern', 'Schweißen', 'sonstiges (Eur/hour)', 'sonstiges (hour)']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()

# Grenzkosten expander
with st.expander("Grenzkosten"):
    for prop in ['Prüfen , Doku', 'Strahlen / Streichen', 'techn. Bearb.', 'mech. Vorbearb.', 'mech. Bearbeitung', 'Zwischentransporte', 'transporte']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.data[prop] = st.text_input(prompt, value=st.session_state.data[prop]).strip()
#
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

# Add 'Next' button to navigate to 'Dekung Kost' section
# if st.button("Gesamtstunden"):
#     st.write("""# Deckung Gesamtstuden""")
#
# #     st.sidebar.header('User Input values')
#
#
#     # Define user input function for 'Dekung Part 2'
#     def user_input_features():
#         Brennen = st.sidebar.text_input('Please input the value for Brennen in minutes', 0)
#         Schlossern = st.sidebar.text_input('Please input the value for Schlossern in minutes', 0)
#         Schweißen = st.sidebar.text_input('Please input the value for Schweißen in minutes', 0)
#         sonstiges = st.sidebar.text_input('Please input the value for sonstiges in minutes', 0)
#
#         data = {'Brennen': float(Brennen),
#                 'Schlossern': float(Schlossern),
#                 'sonstiges': float(sonstiges),
#                 'Schweißen': float(Schweißen)}
#         features = pd.DataFrame(data, index=[0])
#         return features
#
#
#     # Store user input data for 'Dekung Part 2'
#     df_part_2 = user_input_features()
#     st.subheader('The final calculated values are:')
#     st.write(df_part_2)
#
# # Add 'Next' button to navigate to 'Dekung Kost' section
# if st.button("Grenzkosten"):
#     st.write("""# Deckung Grenzkosten""")
#
#     # Go to 'Dekung Kost' section
#     st.sidebar.header('User Input values')
#
#
#     # Function for user input in 'Dekung Kost' section
#     def user_input_features_kost():
#
#         Prüfen_Doku = st.sidebar.text_input('Please input the value for Prüfen , Doku', 0)
#         Strahlen_Streichen = st.sidebar.text_input('Please input the value for Strahlen / Streichen', 0)
#         techn_Bearb = st.sidebar.text_input('Please input the value for techn. Bearb.', 0)
#         mech_Vorbearb = st.sidebar.text_input('Please input the value for mech. Vorbearb.', 0)
#         mech_Bearbeitung = st.sidebar.text_input('Please input the value for mech. Bearbeitung', 0)
#         Zwischentransporte = st.sidebar.text_input('Please input the value for Zwischentransporte', 0)
#         Transporte = st.sidebar.text_input('Please input the value for transporte', 0)
#
#         data = {'Prüfen_Doku': float(Prüfen_Doku),
#                 'Strahlen_Streichen': float(Strahlen_Streichen),
#                 'techn_Bearb': float(techn_Bearb),
#                 'mech_Vorbearb': float(mech_Vorbearb),
#                 'mech_Bearbeitung': float(mech_Bearbeitung),
#                 'Zwischentransporte': float(Zwischentransporte),
#                 'Transporte': float(Transporte)}
#         features = pd.DataFrame(data, index=[0])
#         return features
#
#
#     # Call the function for user input in 'Dekung Kost' section
#     df_kost = user_input_features_kost()
#     st.subheader('The final calculated values are:')
#     st.write(df_kost)
#
#     # Add an option to upload an image in 'Dekung Kost' section
#     uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
#
#     # Download buttons for 'Dekung Kost'
#     if st.button("Download Excel"):
#         output = io.BytesIO()
#         with open("data_kost.xlsx", "wb") as f:
#             df_kost.to_excel(output, index=False)
#             f.write(output.read())
#         st.download_button("Download Excel File", output, key="download_excel_kost", file_name="data_kost.xlsx",
#                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
#
#     if st.button("Download JSON"):
#         json_data = df_kost.to_json(orient="records")
#         st.download_button("Download JSON File", json_data, file_name="data_kost.json", mime="application/json")
