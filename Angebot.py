import streamlit as st
import pandas as pd
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

# Initialize Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


def get_customers():
    customers_ref = db.collection('Customers')
    return [doc.id for doc in customers_ref.stream()]


def get_customer_details(customer_id):
    doc_ref = db.collection('Customers').document(customer_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None


st.title("ATA Angebot App")
col1, col2, col3 = st.columns([1, 6, 4])
with col1:
    st.write("")
with col2:
    st.write("")
with col3:
    image = Image.open('logo_ata.png')
    st.image(image, caption='Ata Logo', width=200)
    ata_address = "A.T.A.\nAnlagentechnik Aschersleben\nErnst-Schiess-Str. 12\n06449 Aschersleben"
    st.text(ata_address)

# image = Image.open('logo_ata.png')
# st.image(image, caption='Ata Logo', width=200)
col4, col5 = st.columns(2)
with col4:
    ata_address = "A.T.A. Anlagentechnik Aschersleben\nErnst-Schiess-Str. 12\n06449 Aschersleben"
    st.text(ata_address)

    # Fetch and display customer names in a dropdown
    customer_names = get_customers()
    selected_customer = st.sidebar.selectbox("Customer", customer_names)

    # Fetch and display the details for the selected customer
    if selected_customer:
        st.write("Kunden Name:", selected_customer)
        customer_details = get_customer_details(selected_customer)
        if customer_details:
            # Display the customer details
            for key, value in customer_details.items():
                st.text(f"{key}: {value}")
        else:
            st.error("Selected customer details not found.")

with col5:
    datum = st.date_input("Datum", None, key='datum')
    angebotsnummer = st.text_input("Angebotsnummer")
    ihre_anfrage = st.text_input("Ihre Anfrage")

st.header("Angebot")
col6, col7, col8, col9, col10, col11, col12, col13 = st.columns([2, 2, 6, 2, 2, 4, 2, 4])
with col6:
    pos = st.text_input("Pos")
with col7:
    artikel = st.text_input("Artikel")
with col8:
    bezeichnung = st.text_area("Bezeichnung", height=75)
with col9:
    menge = st.number_input("Menge")
with col10:
    einh = st.text_input("Einh.")
with col11:
    einzelpreis = st.number_input("Einzelpreis €")
with col12:
    percent = st.number_input("%")
with col13:
    gesamtpreis = st.number_input("Gesamtpreis €")

st.text_input("Hello")