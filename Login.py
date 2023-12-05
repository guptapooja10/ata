import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('anlagentechnik-aschersleben-fd030234653c.json')
firebase_admin.initialize_app(cred)

# Check if Firebase app is not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('anlagentechnik-aschersleben-fd030234653c.json')
    firebase_admin.initialize_app(cred)


def login_app():
    st.title('Welcome to :violet[ATA]')

    choice = st.selectbox('Login/Signup', ['Login', 'Signup'])
    if choice == 'Login':
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')

        st.button('Login')

    else:
        email = st.text_input('E-Mail Address')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your username')

        if st.button('Create my account'):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success('Account created successfully!')
            st.markdown('You can now login using your E-Mail and Password')
            st.balloons()
