import streamlit as st
import pandas as pd
# import pandas_bokeh
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from VK_ST_0 import get_all_collections, get_data_from_firestore, field_mapping, upload_data_to_firestore
import streamlit_antd_components as sac


sac.segmented(

        items=[
            sac.SegmentedItem(label='Deckung', href='https://deckung.streamlit.app/'),
            # sac.SegmentedItem(label='About', href='https://aboutpage.streamlit.app/'),
            # sac.SegmentedItem(label='Sign In', href='https://credentials-page.streamlit.app/'),
            sac.SegmentedItem(label='Project Instantiation', href='https://ata-app-navigator.streamlit.app/'),
            sac.SegmentedItem(label='Material List', href='https://vk-st-0.streamlit.app/'),
            sac.SegmentedItem(label='Schweißen', href='https://ata-vk-0.streamlit.app/'),
            sac.SegmentedItem(label='Angebot', href='https://angebot.streamlit.app/'),
            sac.SegmentedItem(label='Project Status', href='https://ata-project-status.streamlit.app/'), ],
        align='end', size='sm', bg_color='transparent'
    )
# Initialize Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)



# Upload image
uploaded_file = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])


# Function to safely convert a value to float
def try_convert_to_float(value, default=0.0):
    try:
        return float(value) if value else default
    except ValueError:
        return default


# Define data types and properties
deckung_properties = {
    'Kunde': str,
    'Benennung': str,
    'Zeichnungs- Nr.': str,
    'Ausführen Nr.': str,
    'Gewicht': float,
    'Material Kosten': float,
    'Glühen': float,
    'Prüfen , Doku': float,
    'Strahlen / Streichen': float,
    'techn. Bearb.': float,
    'mech. Vorbearb.': float,
    'mech. Bearbeitung': float,
    'Zwischentransporte': float,
    'transporte': float,
    'Grenzkosten': float,
    'Erlös': float,
    'DB': float,
    'Deckungsbeitrag': float,
}


units = {
    'Gewicht': 'kg',
    'Material Kosten': '€',
    'Prüfen , Doku': '€',
    'Strahlen / Streichen': '€',
    'techn. Bearb.': '€',
    'mech. Vorbearb.': '€',
    'mech. Bearbeitung': '€',
    'Zwischentransporte': '€',
    'transporte': '€',
    'Grenzkosten': '€',
    'Erlös': '€',
    'DB': '%',
    'Deckungsbeitrag': '€',
}

vk_st_0_field_mapping = {
    "Gewicht": "Fertigung Gesamt"
}

material_cost_field_mapping = {
    "bis 90mm Einsatz": ("0 – 80mm", "Calculated Weight(Kg)"),
    "bis 90mm Fertig": ("0 – 80mm", "Delivery Weight(Kg)"),
    "bis 90mm Preis": ("0 – 80mm", "Price(€)"),
    "ab 100mm Einsatz": ("80 – 170mm", "Calculated Weight(Kg)"),
    "ab 100mm Fertig": ("80 – 170mm", "Delivery Weight(Kg)"),
    "ab 100mm Preis": ("80 – 170mm", "Price(€)"),
    "Profile Einsatz": ("Profile, Rohre etc.", "Calculated Weight(Kg)"),
    "Profile fertig": ("Profile, Rohre etc.", "Delivery Weight(Kg)"),
    "Profile Preis": ("Profile, Rohre etc.", "Price(€)")
}

# Initialize session state for each property
if "deckung_data" not in st.session_state:
    st.session_state.deckung_data = {prop: "" for prop in deckung_properties}

if 'Material' not in st.session_state:
    # Initialize 'df' with an empty DataFrame or default values if not in session state
    st.session_state['Material'] = pd.DataFrame(
        index=["0 – 80mm", "80 – 170mm", "Profile, Rohre etc.", "Schrauben, Schild", "Zuschlag", "Total"],
        columns=["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)", "Price per Kg(€/Kg)"]
    ).to_dict(orient='index')

#if 'Gesamtstunden' not in st.session_state:
#     st.session_state['Gesamtstunden'] = pd.DataFrame(
#         index=["Brennen", "Schlossern", "Schweißen", "sonstiges", "Gesamt", "Stunden/Tonne", "Fertigung EUR"],
#         columns=["Eur/hour", "Stunden", "Total_Stunden/Tonne"]
#     ).to_dict(orient='index')

# Initialize session state for Erlös, Deckungsbeitrag, and DB if not already initialized
if "Erlös" not in st.session_state:
    st.session_state.erlos = 0.0

if "Deckungsbeitrag" not in st.session_state:
    st.session_state.deckungsbeitrag = 0.0

if "DB (%)" not in st.session_state:
    st.session_state.db_percentage = 0.0

# if 'Gesamtstunden' not in st.session_state:
#     st.session_state['Gesamtstunden'] = {}

# Now 'df' is defined from the session state
df = pd.DataFrame.from_dict(st.session_state['Material']).transpose()
#try:
#    df1 = pd.DataFrame.from_dict(st.session_state['Gesamtstunden']).transpose()
#except Exception as e:
#    print("Error:", e)


if 'total_material_cost' not in st.session_state:
    st.session_state['total_material_cost'] = 0.0

if 'current_collection' not in st.session_state:
    st.session_state.current_collection = None

collection_names = get_all_collections(db)
selected_collection = st.sidebar.selectbox('Select Collection:', options=collection_names, key="Deckung")

if st.session_state.current_collection != selected_collection:
    st.session_state.current_collection = selected_collection
    st.session_state['deckung_data'] = {prop: "" for prop in deckung_properties}  # Reset deckung_data
    st.session_state.erlos = 0.0  # Reset to default or fetch new value
    st.session_state.deckungsbeitrag = 0.0  # Reset to default or fetch new value
    st.session_state.db_percentage = 0.0  # Reset to default or fetch new value
    # Load new data from Firestore for the selected collection
    if selected_collection:
        existing_deckung_data = get_data_from_firestore(selected_collection, 'Deckung')
        if existing_deckung_data:
            # Update session state with existing data
            for key, value in existing_deckung_data.items():
                if key in st.session_state.deckung_data:
                    st.session_state.deckung_data[key] = value
                    # st.write(f"{key}: {value}")
            # st.write("Debug - Updated Session State:", st.session_state.deckung_data)
        details_data = get_data_from_firestore(selected_collection, 'Details')
        if details_data:
            for app_field, firestore_field in field_mapping.items():
                st.session_state.deckung_data[app_field] = details_data.get(firestore_field, "")
        vk_st_0_data = get_data_from_firestore(selected_collection, 'VK-ST-0')
        if vk_st_0_data:
            for app_field, firestore_field in vk_st_0_field_mapping.items():
                st.session_state.deckung_data[app_field] = vk_st_0_data.get(firestore_field, "")
            for firestore_field, (row_index, column_name) in material_cost_field_mapping.items():
                if firestore_field in vk_st_0_data:
                    value = float(vk_st_0_data[firestore_field]) if vk_st_0_data[firestore_field] else 0.0
                    df.at[row_index, column_name] = value
            st.session_state['Material'] = df.to_dict(orient="index")
        try:
            deckungsbeitrag_data = get_data_from_firestore(selected_collection, 'Deckung')

            if deckungsbeitrag_data:
                # Safely convert to float, default to 0.0 if conversion fails
                st.session_state.erlos = try_convert_to_float(deckungsbeitrag_data.get('Erlös', 0.0))
                st.session_state.deckungsbeitrag = try_convert_to_float(
                    deckungsbeitrag_data.get('Deckungsbeitrag', 0.0))
                st.session_state.Gesamtstunden = try_convert_to_float(deckungsbeitrag_data.get('Gesamtstunden', 0.0))
                # Debugging
                # st.write("Deckungsbeitrag from DB:", st.session_state.deckungsbeitrag)
                st.session_state.db_percentage = try_convert_to_float(deckungsbeitrag_data.get('DB (%)', 0.0))
            else:
                st.write("No data found for the selected collection.")

            # Debugging: Display the fetched data
            # st.write("Fetched Data:", deckungsbeitrag_data)

        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")

# st.write("Current Selection:", selected_collection)
# st.write("Session State Collection:", st.session_state.current_collection)

st.title("Deckung")

# Project Details Expander
with st.expander("Project Details"):
    for prop in ['Kunde', 'Benennung', 'Zeichnungs- Nr.', 'Ausführen Nr.']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, key=f"{prop}_input",
                                                            value=st.session_state.deckung_data[prop]).strip()


# Product Details Expander
with st.expander("Product Details"):
    for prop in ['Gewicht', 'Material Kosten']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        if prop == 'Material Kosten':
            # Default to the stored total cost if available, otherwise use the current value
            default_value = st.session_state.get('total_material_cost', float(st.session_state.deckung_data[prop]) if
            st.session_state.deckung_data[prop] else 0.0)
            st.session_state.deckung_data[prop] = st.number_input(prompt, key=f"{prop}_input", value=default_value,
                                                                  step=0.1)
        elif deckung_properties[prop] == float:
            current_value = float(st.session_state.deckung_data[prop]) if st.session_state.deckung_data[prop] else 0.0
            st.session_state.deckung_data[prop] = st.number_input(prompt, key=f"{prop}_input", value=current_value,
                                                                  step=0.1)

        else:
            st.session_state.deckung_data[prop] = st.text_input(prompt,
                                                                key=f"{prop}_input",
                                                                value=st.session_state.deckung_data[prop]).strip()

with st.expander("Material Cost Details"):
    # Display the DataFrame using Streamlit's dataframe function
    st.dataframe(df)

    if st.button('Calculate Totals', key="Calculate_Totals"):
        df = pd.DataFrame.from_dict(st.session_state['Material']).transpose()

        # Convert the DataFrame columns to numeric values where possible
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        # Compute the total for each column (excluding "Price per kg") and update the "Total" row values
        df.loc["Total", ["Calculated Weight(Kg)", "Delivery Weight(Kg)", "Price(€)"]] = df.loc[
                                                                                        :"Zuschlag",
                                                                                        ["Calculated Weight(Kg)",
                                                                                         "Delivery Weight(Kg)",
                                                                                         "Price(€)"]].sum()
        # Update the session state with the edited DataFrame
        st.session_state['Material'] = df.to_dict(orient="index")

        # Store the total material cost in session state
        st.session_state['total_material_cost'] = df.loc["Total", "Price(€)"]

        # Update the "Material Kosten" in "Product Details" if it's already been rendered
        if 'Material Kosten' in st.session_state.deckung_data:
            st.session_state.deckung_data['Material Kosten'] = st.session_state['total_material_cost']  # this is where the Material Kosten is being used

with st.expander("Deckungsbeitrag"):
    # Input fields
    # st.session_state.erlos = float(st.session_state.erlos) if st.session_state.erlos else 0.0
    st.session_state.erlos = st.number_input("Erlös", value=st.session_state.erlos)
    # st.session_state.db_percentage = float(st.session_state.db_percentage) if st.session_state.db_percentage else 0.0
    st.session_state.db_percentage = st.number_input("DB (%)", value=st.session_state.db_percentage, step=0.01)
    # st.session_state.deckungsbeitrag = float(st.session_state.deckungsbeitrag) if st.session_state.deckungsbeitrag
    # else 0.0
    st.session_state.deckungsbeitrag = st.number_input("Deckungsbeitrag", value=st.session_state.deckungsbeitrag)
    st.write("Deckungsbeitrag in UI:", st.session_state.deckungsbeitrag)


# Fetch values from Firestore for VK-0 document
vk_0_data = get_data_from_firestore(selected_collection, 'VK-0')
if vk_0_data:
    # Update session state with VK-0 data
    st.session_state.deckung_data['Brennen_VK_0'] = vk_0_data.get('Brennen_VK_0', "")
    st.session_state.deckung_data['Schlossern_VK_0'] = vk_0_data.get('Schlossern_VK_0', "")
    st.session_state.deckung_data['Schweißen_VK_0'] = vk_0_data.get('Schweißen_VK_0', "")


brennen_col = 'Brennen'
eur_hour_col = 'Eur/hour'
stunden_col = 'Stunden'
total_stunden_tonne_col = 'Total_Stunden/Tonne'

df1 = pd.DataFrame([
    {"Process": "Brennen", "Eur/hour": 0, "Hour": st.session_state.deckung_data.get('Brennen_VK_0', 0)},
    {"Process": "Schlossern", "Eur/hour": 0, "Hour": st.session_state.deckung_data.get('Schlossern_VK_0', 0)},
    {"Process": "Schweißen", "Eur/hour": 0, "Hour": st.session_state.deckung_data.get('Schweißen_VK_0', 0)},
    {"Process": "sonstiges", "Eur/hour": 0, "Hour": 0},
])
# Define the DataFrame with the "Total" column calculated as the product of "Eur/hour" and "Hour"
with st.expander("Processing Time"):
    gewicht_value = st.session_state.deckung_data.get('Gewicht', 0)
    st.text_input("Gewicht", value=st.session_state.deckung_data["Gewicht"])
    for index, row in df1.iterrows():
        row["Eur/hour"] = st.number_input(f"Eur/hour for {row['Process']}", value=row["Eur/hour"])

    edited_df = st.data_editor(df1, num_rows="dynamic")

    if st.button("Calculate Total Time"):
        gesamtstunden = df1["Hour"].sum()  # Sum of hours for all processes
        stunden_tonne = gesamtstunden / gewicht_value * 1000  # Hours per tonne
        df1["Fertigung_EUR"] = df1["Eur/hour"] * df1["Hour"]  # Calculate Fertigung_EUR
        fertigung_eur_total = df1["Fertigung_EUR"].sum()  # Sum of Fertigung_EUR
        st.session_state.deckung_data["Gesamtstunden"] = gesamtstunden
        st.session_state.deckung_data["Stunden / Tonne"] = stunden_tonne
        # Display the calculated results
        st.text_input("Gesamtstunden", value=gesamtstunden)
        st.text_input("Stunden / Tonne", value=stunden_tonne)
        st.text_input("Fertigung_EUR_Total", value=fertigung_eur_total)

# Create an expander for 'Grenzkosten'
with st.expander("Grenzkosten"):
    for prop in ['Glühen', 'Prüfen , Doku', 'Strahlen / Streichen', 'techn. Bearb.', 'mech. Vorbearb.',
                 'mech. Bearbeitung',
                 'Zwischentransporte', 'transporte']:
        prompt = f"{prop}"
        if prop in units:
            prompt += f" ({units[prop]})"
        st.session_state.deckung_data[prop] = st.text_input(prompt, value=st.session_state.deckung_data[prop]).strip()


    # Total calculation
    def grenz_calculate(data):
        numeric_fields = ['Glühen', 'Prüfen , Doku', 'Strahlen / Streichen', 'techn. Bearb.', 'mech. Vorbearb.',
                          'mech. Bearbeitung',
                          'Zwischentransporte', 'transporte', 'Material Kosten']

        for field in numeric_fields:
            data[field] = float(data[field]) if data[field] else 0.0

        # Access 'Fertigung EUR' from session state
        data['fertigung_eur'] = st.session_state.get('fertigung_eur', 0.0)
        data['Grenzkosten'] = data['fertigung_eur'] + data['Material Kosten'] + data['Glühen'] + data['Prüfen , Doku'] + data['Strahlen / Streichen'] + data['techn. Bearb.'] + data['mech. Vorbearb.'] + data['mech. Bearbeitung'] + data['Zwischentransporte'] + data['transporte']
        return data


    # Calculate Grenzkosten directly without a button
    grenz_data = grenz_calculate(st.session_state.deckung_data)

    # Display the calculated Grenzkosten
    st.write("Calculated Grenzkosten:", grenz_data['Grenzkosten'])

# Combine data for downloads
combined_data = {
    **st.session_state.deckung_data,  # Project and Product Details
    **st.session_state['Material'],  # Material Cost Details
    # **st.session_state['Gesamtstunden'],
    'Erlös': st.session_state.erlos,
    'DB (%)': st.session_state.db_percentage,
    'Deckungsbeitrag': st.session_state.deckungsbeitrag,
}

# Convert the combined data to a pandas DataFrame
df = pd.DataFrame([combined_data])

# Add a button to download the data as Excel
if st.button("Download as Excel", key="Deckung_Excel"):
    # Convert relevant values to numeric types
    # hourly_rate = pd.to_numeric(st.session_state.deckung_data['sonstiges (Eur/hour)'], errors='coerce')
    # hours = pd.to_numeric(st.session_state.deckung_data['sonstiges (hour)'], errors='coerce')
    # Create a dictionary with the data
    data_dict = {
        'Kunde': st.session_state.deckung_data['Kunde'],
        'Benennung': st.session_state.deckung_data['Benennung'],
        'Anfr. Nr.': st.session_state.deckung_data['Zeichnungs- Nr.'],
        'Gewicht': st.session_state.deckung_data['Gewicht'],
        'Material': st.session_state.deckung_data['Material Kosten'],
        # 'Brennen_Deckung': st.session_state.deckung_data['Brennen_Deckung'],
        # 'Schlossern_Deckung': st.session_state.deckung_data['Schlossern_Deckung'],
        # 'Schweißen_Deckung': st.session_state.deckung_data['Schweißen_Deckung'],
        # 'sonstiges': hourly_rate * hours,
        # # # 'Gesamtstunden': (
        # #         st.session_state.deckung_data['Brennen_Deckung'] +
        # #         st.session_state.deckung_data['Schlossern_Deckung'] +
        # #         st.session_state.deckung_data['Schweißen_Deckung'] +
        # #         st.session_state.deckung_data['sonstiges (hour)'] +
        # #         st.session_state.deckung_data['sonstiges (Eur/hour)']
        # ),
        # 'Stunden / Tonne': 0 if st.session_state.deckung_data['Gewicht'] == 0 else st.session_state.deckung_data[
        #                                                                                'Gesamtstunden'] /
        #                                                                            st.session_state.deckung_data[
        #                                                                                'Gewicht'],
        # 'Fertigung EUR': (
        #         st.session_state.deckung_data['Brennen_Deckung'] +
        #         st.session_state.deckung_data['Schlossern_Deckung'] +
        #         st.session_state.deckung_data['Schweißen_Deckung'] +
        #         st.session_state.deckung_data['sonstiges (hour)'] +
        #         st.session_state.deckung_data['sonstiges (Eur/hour)']
        # ),
        'Glühen': 0,
        'Prüfen , Doku': st.session_state.deckung_data['Prüfen , Doku'],
        'Strahlen / Streichen': st.session_state.deckung_data['Strahlen / Streichen'],
        'techn. Bearb.': st.session_state.deckung_data['techn. Bearb.'],
        'mech. Vorbearb.': st.session_state.deckung_data['mech. Vorbearb.'],
        'mech. Bearbeitung': st.session_state.deckung_data['mech. Bearbeitung'],
        'Zwischentransporte': st.session_state.deckung_data['Zwischentransporte'],
        'Transporte': st.session_state.deckung_data['transporte'],
        'Grenzkosten': (
                st.session_state.deckung_data['Prüfen , Doku'] +
                st.session_state.deckung_data['Strahlen / Streichen'] +
                st.session_state.deckung_data['techn. Bearb.'] +
                st.session_state.deckung_data['mech. Vorbearb.'] +
                st.session_state.deckung_data['mech. Bearbeitung'] +
                st.session_state.deckung_data['Zwischentransporte'] +
                st.session_state.deckung_data['transporte']
        ),
        'Erlös': st.session_state.erlos,
        'DB': st.session_state.deckungsbeitrag,
        'Soll 10%': st.session_state.erlos * 0.1,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag
    }
    data_dict.update({
        'Erlös': st.session_state.erlos,
        'DB (%)': st.session_state.db_percentage,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag,
        'Soll 10%': st.session_state.erlos * 0.1
    })

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
if st.button("Download as JSON", key="Deckung_json"):
    # Convert the DataFrame to JSON
    json_data = df.to_json(orient="records")

    # Download the JSON file using st.download_button
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

if st.button("Upload to Database", key="upload_to_db"):
    # Prepare the data to upload
    combined_data_to_upload = {
        **st.session_state.deckung_data,  # Project and Product Details
        **st.session_state['Material'],  # Material Cost Details
        #**st.session_state['Gesamtstunden'],
        'Erlös': st.session_state.erlos,
        'DB (%)': st.session_state.db_percentage,
        'Deckungsbeitrag': st.session_state.deckungsbeitrag,
        #'total_stunden': st.session_state['Gesamtstunden'].get('Gesamtstunden', {}).get('Stunden', 0),
        #'stunden_tonne': st.session_state['Gesamtstunden'].get('Stunden/Tonne', {}).get(total_stunden_tonne_col, 0),
        #'fertigung_eur': st.session_state['Gesamtstunden'].get('Fertigung EUR', {}).get(stunden_col, 0),
    }

    # Call the function to upload data to Firestore
    try:
        upload_data_to_firestore(db, selected_collection, "Deckung", combined_data_to_upload)

    except Exception as e:
        st.error(f"An error occurred: {e}")
