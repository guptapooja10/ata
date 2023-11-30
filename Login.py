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

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)

# Initialize Firestore client
key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(
    key_dict, client_email=key_dict["client_email"], token_uri=key_dict["token_uri"]
)
db = firestore.Client(credentials=creds)


# Registering new users
def register_users(user_id, name, email, password):
    user_ref = db.collection('Users').document(user_id)
    user_ref.set({
        'name': name,
        'email': email,
        'password': password
    })


action = st.radio('Select Action:', ['Register', 'Login'])

if action == 'Register':
    st.subheader('Register')
    user_id = st.text_input('User ID:')
    name = st.text_input('Name:')
    email = st.text_input('E-Mail:')
    password = st.text_input('Password:', type='password')

    if st.button('Register'):
        register_users(user_id, name, email, password)
        st.success("Registration successful!")
