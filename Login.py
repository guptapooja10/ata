import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from PIL import Image
import firebase_admin
from firebase_admin import credentials, auth

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

# Initialize Firebase Admin SDK
firebase_cred = credentials.Certificate(key_dict)
firebase_admin.initialize_app(firebase_cred)

def register_user(email, password):
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(email=email, password=password)
        # Store user details in Firestore
        user_ref = db.collection('users').document(user.uid)
        user_ref.set({
            'email': email,
            'uid': user.uid
        })
        return user
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return None

def login_user(email, password):
    try:
        # Authenticate user using Firebase Authentication
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None

def main():
    st.title("Firebase Authentication Demo")

    page = st.sidebar.selectbox("Select Page", ["Login", "Register"])

    if page == "Login":
        st.header("Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(login_email, login_password)
            if user:
                st.success("Login successful!")
                st.write(f"Welcome, {user['email']} (UID: {user['localId']})")

    elif page == "Register":
        st.header("Register")
        register_email = st.text_input("Email")
        register_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if register_password == confirm_password:
                user = register_user(register_email, register_password)
                if user:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Error during registration. Please try again.")
            else:
                st.error("Passwords do not match. Please try again.")

if __name__ == "__main__":
    main()
