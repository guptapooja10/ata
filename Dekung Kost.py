import streamlit as st
import pandas as pd
import io

st.write("""# Deckung Grenzkosten""")

st.sidebar.header('User Input values')


def user_input_features():
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


df = user_input_features()
st.subheader('The final calculated values are:')
st.write(df)


if st.button("Download Excel"):
    output = io.BytesIO()
    with open("data.xlsx", "wb") as f:
        df.to_excel(output, index=False)
        f.write(output.read())
    st.download_button("Download Excel File", output, key="download_excel", file_name="data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if st.button("Download JSON"):
    json_data = df.to_json(orient="records")
    st.download_button("Download JSON File", json_data, file_name="data.json", mime="application/json")

