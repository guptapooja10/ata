import streamlit as st
import pandas as pd
import io

st.write("""# Deckung Gesamtstuden""")

st.sidebar.header('User Input values')


def user_input_features():
    Brennen = st.sidebar.text_input('Please input the value for Brennen in minutes', 0)
    Schlossern = st.sidebar.text_input('Please input the value for Schlossern in minutes', 0)
    Schweißen = st.sidebar.text_input('Please input the value for Schweißen in minutes', 0)
    sonstiges = st.sidebar.text_input('Please input the value for sonstiges in minutes', 0)
    # Schweißen = st.sidebar.text_input('Please input the value for Schweißen in minutes', 0)

    data = {'Brennen': float(Brennen),
            'Schlossern': float(Schlossern),
            'sonstiges': float(sonstiges),
            'Schweißen': float(Schweißen)}
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
