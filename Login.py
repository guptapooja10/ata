import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth
import os
import tempfile

# Initialize Firebase app if not already initialized
initialize_firebase_app()


def get_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'page' not in st.session_state:
        st.session_state.page = 'login'


# Call get_session_state before any Streamlit function
get_session_state()


def login_app():
    st.title('Welcome to :violet[ATA]')

    if st.session_state.page == 'login':
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            # Assuming authentication is successful, set st.session_state.authenticated to True
            st.session_state.authenticated = True
            # Change the page to 'file_upload'
            st.session_state.page = 'file_upload'

    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success('Account created successfully!')
            st.markdown('You can now log in using your E-Mail and Password')
            st.balloons()


def file_upload_page():
    st.header('File Upload Page')
    st.write("Upload your important documents here:")

    uploaded_files = st.file_uploader("Choose a file", type=["pdf", "txt", "csv", "xlsx"])

    if uploaded_files is not None:
        st.success("File uploaded successfully!")

        # Process the uploaded file as needed
        # For example, you can save it to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_files.read())
            st.write("Temporary file saved at:", temp_file.name)

        # Clean up the temporary file
        os.remove(temp_file.name)


if __name__ == "__main__":
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call login_app after get_session_state
    login_app()

    # Handle navigation or display other pages based on authentication status
    if st.session_state.authenticated:
        # Display file upload functionality based on the current page state
        if st.session_state.page == 'file_upload':
            file_upload_page()
