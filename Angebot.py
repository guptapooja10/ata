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


def reset_rows():
    # Explicitly set all inputs to their default values
    for i in range(1, st.session_state['rows'] + 1):
        st.session_state[f'input_pos_{i}'] = ''
        st.session_state[f'input_artikel_{i}'] = ''
        st.session_state[f'input_bezeichnung_{i}'] = ''
        st.session_state[f'input_menge_{i}'] = 0  # Assuming 0 is a valid default for 'Menge'
        st.session_state[f'input_einh_{i}'] = ''
        st.session_state[f'input_einzelpreis_{i}'] = 0.0  # Assuming 0.0 is a valid default for 'Einzelpreis'
        st.session_state[f'input_percent_{i}'] = 0.0  # Assuming 0.0 is a valid default for 'Percent'
        st.session_state[f'input_gesamtpreis_{i}'] = 0.0  # Assuming 0.0 is a valid default for 'Gesamtpreis'
    st.session_state['rows'] = 1

    st.session_state['datum'] = None
    st.session_state['angebotsnummer'] = ''
    st.session_state['ihre_anfrage'] = ''
    st.session_state['zahlung'] = ''
    st.session_state['lieferung'] = ''
    st.session_state['lieferdatum'] = None
    st.session_state['steuer_nr'] = ''
    st.session_state['ust_id_nr'] = ''
    st.session_state['angebot_gueltig_bis'] = None


st.title("ATA Angebot App")

col1, col2, col3 = st.columns([1, 6, 4])
with col3:
    image = Image.open('logo_ata.png')
    st.image(image, caption='Ata Logo', width=200)
    ata_address = "A.T.A.\nAnlagentechnik Aschersleben\nErnst-Schiess-Str. 12\n06449 Aschersleben"
    st.text(ata_address)

customer_names = get_customers()
selected_customer = st.selectbox("Customer", customer_names, index=0, key='selected_customer')

if 'last_selected_customer' not in st.session_state:
    st.session_state['last_selected_customer'] = selected_customer

if st.session_state['last_selected_customer'] != selected_customer:
    st.session_state['last_selected_customer'] = selected_customer
    reset_rows()

col4, col5 = st.columns(2)
with col4:
    ata_address = "A.T.A. Anlagentechnik Aschersleben\nErnst-Schiess-Str. 12\n06449 Aschersleben"
    st.text(ata_address)

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
    angebotsnummer = st.text_input("Angebotsnummer", key='angebotsnummer')
    ihre_anfrage = st.text_input("Ihre Anfrage", key='ihre_anfrage')

st.header("Angebot")


def display_row(row_num):
    cols = st.columns([2, 2, 6, 2, 2, 4, 2, 4])
    with cols[0]:
        pos = st.text_input(f"Pos", key=f"input_pos_{row_num}")
    with cols[1]:
        artikel = st.text_input(f"Artikel", key=f"input_artikel_{row_num}")
    with cols[2]:
        bezeichnung = st.text_input(f"Bezeichnung", key=f"input_bezeichnung_{row_num}")
    with cols[3]:
        menge = st.number_input(f"Menge", min_value=0.0, format="%f", key=f"input_menge_{row_num}")
    with cols[4]:
        einh = st.text_input(f"Einh.", key=f"input_einh_{row_num}")
    with cols[5]:
        einzelpreis = st.number_input(f"Einzelpreis € ", min_value=0.0, format="%f",
                                      key=f"input_einzelpreis_{row_num}")
    with cols[6]:
        percent = st.number_input(f"%", min_value=0.0, format="%f", key=f"input_percent_{row_num}")
    with cols[7]:
        gesamtpreis = st.number_input(f"Gesamtpreis €", min_value=0.0, format="%f",
                                      key=f"input_gesamtpreis_{row_num}")
        return gesamtpreis


# Function to calculate the total 'Gesamtpreis' (Nettosumme)
def calculate_nettosumme():
    return sum(st.session_state.get(f'input_gesamtpreis_{i}', 0.0) for i in range(1, st.session_state['rows'] + 1))


# Function to calculate the VAT amount based on the Nettosumme
def calculate_vat(netto_summe, vat_rate=19.0):
    return netto_summe * (vat_rate / 100)


if 'rows' not in st.session_state:
    st.session_state['rows'] = 1

gesamtpreis_values = []
for row_num in range(1, st.session_state['rows'] + 1):
    gesamtpreis = display_row(row_num)
    gesamtpreis_values.append(gesamtpreis)

if st.button('Add Row'):
    st.session_state['rows'] += 1

nett_summe = calculate_nettosumme()
st.session_state['nettosumme'] = nett_summe
vat_amount = calculate_vat(nett_summe)

col6, col7 = st.columns(2)

with col6:
    st.header("Weitere Details")

    # Payment, delivery, and other details
    zahlung = st.text_input("Zahlung", key='zahlung')
    lieferung = st.text_input("Lieferung", key='lieferung')
    lieferdatum = st.date_input("Lieferdatum", None, key='lieferdatum')
    steuer_nr = st.text_input("St.Nr.", key='steuer_nr')
    ust_id_nr = st.text_input("USt-IdNr.", key='ust_id_nr')

with col7:
    st.header("Summen")

    # Totals
    st.write(f"Nettosumme: {nett_summe:.2f} €")
    st.write(f"19 % MwSt: {vat_amount:.2f} €")
    gesamtsumme = nett_summe + vat_amount
    st.session_state['gesamtsumme'] = gesamtsumme
    st.write(f"Gesamtsumme: {gesamtsumme:.2f} €")

# Offer validity
angebot_gueltig_bis = st.date_input("Unser Angebot ist gültig bis :", None, key='angebot_gueltig_bis')
