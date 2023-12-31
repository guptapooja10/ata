import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth

# Initialize Firebase app if not already initialized
initialize_firebase_app()


# To check the user authentication
def get_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False


# Call get_session_state before any Streamlit function
get_session_state()


def navigation_bar():
    apps = {
        "Login page": "https://credentials-page.streamlit.app/",
        "Project Instantiation": "https://ata-app-navigator.streamlit.app/",
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "ATA-Project-Status": "https://ata-project-status.streamlit.app/"
    }

    st.sidebar.title('Navigation')

    if st.session_state.authenticated:
        # If the user is authenticated, display all links
        for app_name, app_url in apps.items():
            st.sidebar.markdown(f"[{app_name}]({app_url})")
    else:
        # If the user is not authenticated, display only the "Login page" link
        st.sidebar.markdown(f"[Login page]({apps['Login page']})")


def login_app():
    st.title('Welcome to :violet[ATA]')

    choice = st.selectbox('Login/Signup', ['Login', 'Signup'])
    if choice == 'Login':
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            # If authentication is successful, set st.session_state.authenticated to True
            st.session_state.authenticated = True
            # st.write('Which app do you want to use?')
            # Display a clickable link to the Project Instantiation app
            # st.experimental_set_query_params(app='project_instantiation')
    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            user = auth.create_user(email=email, password=password, uid=username)
            # If user creation is successful, set st.session_state.authenticated to True
            # st.session_state.authenticated = True
            st.success('Account created successfully!')
            st.markdown('You can now log in using your E-Mail and Password')
            st.balloons()


if __name__ == "__main__":
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call login_app after get_session_state
    login_app()

    # Call navigation_bar after login_app
    navigation_bar()
