import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth, firestore

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

        is_admin_checked = st.checkbox('Admin', key='admin_checkbox')
        is_not_admin_checked = st.checkbox('Not an Admin', key='not_admin_checkbox')

        if is_admin_checked and is_not_admin_checked:
            st.warning("Please select only one option (Admin or Not an Admin)")
        else:
            if email and password:  # Check if email and password are provided
                try:
                    user = auth.get_user_by_email(email)
                    user_data = firestore.client().collection('users').document(user.uid).get().to_dict()

                    if user_data:
                        if (is_admin_checked and user_data['role'] == 'Admin') or \
                                (is_not_admin_checked and user_data['role'] == 'Not Admin'):
                            st.session_state.authenticated = True
                            st.session_state.user_uid = user.uid
                            st.success("Login successful!")

                            if is_admin_checked:
                                st.experimental_set_query_params(app='project_instantiation')
                                st.link_button("Sign In", "https://ata-app-navigator.streamlit.app/")
                            elif is_not_admin_checked:
                                st.experimental_set_query_params(app='Project_Status_App')
                                st.link_button("Sign In", "https://ata-project-status.streamlit.app/")

                        else:
                            st.warning("Incorrect role selected during login.")
                    else:
                        st.warning("User not found. Please sign up first.")
                except:
                    st.warning(f"Authentication failed")
            elif is_admin_checked or is_not_admin_checked:
                st.warning("Please enter both email and password before attempting to sign in.")
    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        role = st.selectbox('Role', ['Admin', 'Not Admin'])
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            try:
                user = auth.create_user(email=email, password=password)
                firestore.client().collection('users').document(user.uid).set({
                    'role': role,
                    'uid': username
                })

                st.success('Account created successfully!')
                st.markdown('You can now log in using your E-Mail and Password')
                st.balloons()
            except:
                st.warning(f"Account creation failed")


if __name__ == "__main__":
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call login_app after get_session_state
    login_app()
