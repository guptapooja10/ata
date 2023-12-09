import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth

# Initialize Firebase app if not already initialized
initialize_firebase_app()


def login_app():
    st.title('Welcome to :violet[ATA]')

    choice = st.selectbox('Login/Signup', ['Login', 'Signup'])
    if choice == 'Login':
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            st.write('Which app do you want to use?')
            # Add the hyperlink to navigate to the Project instantiation app
            st.components.v1.html(
                """
                <script>
                    window.location.href = "https://ata-app-navigator.streamlit.app/";
                </script>
                """
            )

    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success('Account created successfully!')
            st.markdown('You can now log in using your E-Mail and Password')
            st.balloons()


if __name__ == "__main__":
    login_app()
