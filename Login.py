import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from PIL import Image


# Navigation bar
def navigation_bar():
    apps = {
        "Project Instantiation": "https://ata-app-navigator.streamlit.app/",
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",
        "ATA-Dashboard-App": "https://ata-dashboard-app.streamlit.app/"
    }

    st.sidebar.title('Navigation')

    for app_name, app_url in apps.items():
        st.sidebar.markdown(f"[{app_name}]({app_url})")


navigation_bar()
st.title("Login Page")

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Load Firestore credentials from Streamlit secrets
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

