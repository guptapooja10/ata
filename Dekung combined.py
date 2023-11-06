import streamlit as st
import pandas as pd
import io

st.write("""# Deckung Gesamtstuden""")

st.sidebar.header('User Input values')


# Define user input function for 'Dekung Part 2'
def user_input_features():
    Brennen = st.sidebar.text_input('Please input the value for Brennen in minutes', 0)
    Schlossern = st.sidebar.text_input('Please input the value for Schlossern in minutes', 0)
    Schweißen = st.sidebar.text_input('Please input the value for Schweißen in minutes', 0)
    sonstiges = st.sidebar.text_input('Please input the value for sonstiges in minutes', 0)

    data = {'Brennen': float(Brennen),
            'Schlossern': float(Schlossern),
            'sonstiges': float(sonstiges),
            'Schweißen': float(Schweißen)}
    features = pd.DataFrame(data, index=[0])
    return features


# Store user input data for 'Dekung Part 2'
df_part_2 = user_input_features()
st.subheader('The final calculated values are:')
st.write(df_part_2)

# Add 'Next' button to navigate to 'Dekung Kost' section
if st.button("Next"):
    st.write("""# Deckung Grenzkosten""")

    # Go to 'Dekung Kost' section
    st.sidebar.header('User Input values')


    # Function for user input in 'Dekung Kost' section
    def user_input_features_kost():

        Prüfen_Doku = st.sidebar.text_input('Please input the value for Prüfen , Doku', 0)
        Strahlen_Streichen = st.sidebar.text_input('Please input the value for Strahlen / Streichen', 0)
        techn_Bearb = st.sidebar.text_input('Please input the value for techn. Bearb.', 0)
        mech_Vorbearb = st.sidebar.text_input('Please input the value for mech. Vorbearb.', 0)
        mech_Bearbeitung = st.sidebar.text_input('Please input the value for mech. Bearbeitung', 0)
        Zwischentransporte = st.sidebar.text_input('Please input the value for Zwischentransporte', 0)
        Transporte = st.sidebar.text_input('Please input the value for transporte', 0)

        data = {'Prüfen_Doku': float(Prüfen_Doku),
                'Strahlen_Streichen': float(Strahlen_Streichen),
                'techn_Bearb': float(techn_Bearb),
                'mech_Vorbearb': float(mech_Vorbearb),
                'mech_Bearbeitung': float(mech_Bearbeitung),
                'Zwischentransporte': float(Zwischentransporte),
                'Transporte': float(Transporte)}
        features = pd.DataFrame(data, index=[0])
        return features


    # Call the function for user input in 'Dekung Kost' section
    df_kost = user_input_features_kost()
    st.subheader('The final calculated values are:')
    st.write(df_kost)

    # Add an option to upload an image in 'Dekung Kost' section
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    # Download buttons for 'Dekung Kost'
    if st.button("Download Excel"):
        output = io.BytesIO()
        with open("data_kost.xlsx", "wb") as f:
            df_kost.to_excel(output, index=False)
            f.write(output.read())
        st.download_button("Download Excel File", output, key="download_excel_kost", file_name="data_kost.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if st.button("Download JSON"):
        json_data = df_kost.to_json(orient="records")
        st.download_button("Download JSON File", json_data, file_name="data_kost.json", mime="application/json")
