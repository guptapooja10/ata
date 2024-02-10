import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth

# Initialize Firebase app if not already initialized
initialize_firebase_app()

def get_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

# Call get_session_state before any Streamlit function
get_session_state()

def login_app():
    st.title('Welcome to :violet[ATA]')

    choice = st.selectbox('Login/Signup', ['Login', 'Signup'])
    if choice == 'Login':
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')

        # Check if the "Login" button is clicked
        if st.button('Login'):
            # Assuming authentication is successful, set st.session_state.authenticated to True
            st.session_state.authenticated = True

    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success('Account created successfully!')
            st.markdown('You can now log in using your E-Mail and Password')
            st.balloons()

    # Use st.button with conditional rendering for the "Login" functionality
    if not st.session_state.authenticated:
        if st.button('Login'):
            # Redirect to the specified URL if authenticated
            st.experimental_set_query_params(app='project_instantiation')
            st.markdown("[Login](https://ata-app-navigator.streamlit.app/)")

if __name__ == "__main__":
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call login_app after get_session_state
    login_app()
