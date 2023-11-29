import streamlit as st
from google.cloud import firestore
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
db = firestore.Client(project="anlagentechnik-aschersleben")


# Function to register a new user
def register_user(email, password):
    try:
        # Check if the user already exists
        user_ref = db.collection('users').document(email)
        if user_ref.get().exists:
            st.error("User already exists. Please log in.")
            return None

        # Create a new user document in the 'users' collection
        user_ref.set({
            'email': email,
            'password': password
        })
        return user_ref
    except Exception as e:
        st.error(f"Error registering user: {e}")
        return None


# Function to authenticate a user
def login_user(email, password):
    try:
        # Retrieve the user document from the 'users' collection
        user_ref = db.collection('users').document(email)
        user_data = user_ref.get().to_dict()

        # Check if the user exists and the password is correct
        if user_data and user_data.get('password') == password:
            return user_data
        else:
            st.error("Invalid email or password. Please try again.")
            return None
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None


# UI for login and registration
def main():
    st.title("Login Page")

    page = st.sidebar.selectbox("Select Page", ["Login", "Register"])

    if page == "Login":
        st.header("Login")
        login_email = st.text_input("Email")
        login_password = st.text_input("Password", type="password")

        if st.button("Login"):
            user_data = login_user(login_email, login_password)
            if user_data:
                st.success("Login successful!")
                st.write(f"Welcome, {user_data['email']}")
            else:
                st.error("Login failed. Please check your credentials.")

    elif page == "Register":
        st.header("Register")
        register_email = st.text_input("Email")
        register_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if register_password == confirm_password:
                user_ref = register_user(register_email, register_password)
                if user_ref:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error("Error during registration. Please try again.")
            else:
                st.error("Passwords do not match. Please try again.")


if __name__ == "__main__":
    main()
