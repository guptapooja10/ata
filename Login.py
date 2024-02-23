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


def app():
    # Usernm = []
    st.title('Welcome to :violet[Pondering] :sunglasses:')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    email = ""  # Initialize the email variable outside the block

    def f():
        nonlocal email  # Use the nonlocal keyword to access the outer 'email' variable
        try:
            email_input = st.text_input('Email Address')  # Input the email here
            password_input = st.text_input('Password', type='password')

            if st.button('Login'):
                user = auth.get_user_by_email(email_input)
                email = email_input # Update the email variable
                print(user.uid)
                st.session_state.username = user.uid
                st.session_state.useremail = user.email

                global Usernm
                Usernm = (user.uid)

                st.session_state.signedout = True
                st.session_state.signout = True
        except:
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''

    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False

    if not st.session_state["signedout"]:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])

        if choice == 'Sign up':
            email_input = st.text_input("Enter your email")  # Input the email here
            password_input = st.text_input('Password', type='password')
            username = st.text_input("Enter your unique username")

            if st.button('Create my account'):
                try:
                    user = auth.create_user(email=email_input, password=password_input, uid=username)

                    st.success('Account created successfully!')
                    st.markdown('Please Login using your email and password')
                    st.balloons()
                except:
                    st.warning(f"Account creation failed.")
        else:
            f()  # Call the function here

    if st.session_state.signout:
        st.text('Name ' + st.session_state.username)
        st.text('Email id: ' + st.session_state.useremail)
        st.button('Sign out', on_click=t)


if __name__ == "__main__":
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call app after get_session_state
    app()
