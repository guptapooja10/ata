import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

# Initialize Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

# Retrieve data from Firestore
details_ref = db.collection("Details")
details_docs = details_ref.stream()

data = []
for doc in details_docs:
    doc_data = doc.to_dict()
    data.append({
        "Kunde": doc_data.get("Kunde", ""),
        "Zeichnungs-Nr": doc_data.get("Zeichnungs-Nr", "")
    })

# Create a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
st.table(df)
