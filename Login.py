import streamlit as st
from firebase_init import initialize_firebase_app
from firebase_admin import auth
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from Deckung import deckung_properties  # Assuming you have this file with deckung_properties defined

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

        if st.button('Login'):
            # Assuming authentication is successful, set st.session_state.authenticated to True
            st.session_state.authenticated = True
            # Redirect to "Project Instantiation" page
            st.markdown("[Redirecting to Project Instantiation](https://ata-app-navigator.streamlit.app/)")
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


def fetch_customers(db):
    customers_list = []
    customer_docs = db.collection('Customers').stream()
    for doc in customer_docs:
        customers_list.append(doc.id)
    return customers_list


def instantiate_project(kunde, benennung, zeichnungs_nr, ausfuehren_nr, db):
    doc_ref = db.collection(zeichnungs_nr).document('Details')
    doc = doc_ref.get()
    if doc.exists:
        st.success(f"A project with Zeichnungs Nr {zeichnungs_nr} already exists.")
        return False
    else:
        project_data = {
            "Kunde": kunde,
            "Benennung": benennung,
            "Ausführen Nr": ausfuehren_nr,
            "Zeichnungs- Nr.": zeichnungs_nr
        }
        doc_ref.set(project_data)
        st.success(f"Project with Zeichnungs Nr {zeichnungs_nr} created successfully.")
        # After creating the project, update the customer's Project_List
        customer_doc_ref = db.collection('Customers').document(kunde)
        customer_doc = customer_doc_ref.get()
        if customer_doc.exists:
            customer_data = customer_doc.to_dict()
            project_list = customer_data.get('Project_List', [])
            project_list.append(zeichnungs_nr)
            customer_doc_ref.update({'Project_List': project_list})
            st.success(f"Zeichnungs Nr {zeichnungs_nr} added to the customer's Project_List.")
        else:
            st.success(f"The customer {kunde} does not exist in the database.")

        vk_st0_doc_ref = db.collection(zeichnungs_nr).document('VK-ST-0')
        vk_st0_data = {
            "Kunde": "",
            "Gegenstand": "",
            "Zeichnungs- Nr.": "",
            "Ausführen Nr.": "",
            "Fertigung Gesamt": 0,
            "bis 90mm Einsatz": 0,
            "bis 90mm Fertig": 0,
            "bis 90mm Preis": 0,
            "ab 100mm Einsatz": 0,
            "ab 100mm Fertig": 0,
            "ab 100mm Preis": 0,
            "Profile Einsatz": 0,
            "Profile fertig": 0,
            "Profile Preis": 0
        }
        vk_st0_doc_ref.set(vk_st0_data)
        st.success("'VK-ST-0' document created successfully.")

        # Create VK-0 document and add to Firebase
        vk0_doc_ref = db.collection(zeichnungs_nr).document('VK-0')
        vk0_data = {
            "Brennen": 0,
            "Richten": 0,
            "Heften_Zussamenb_Verputzen": 0,
            "Anzeichnen": 0,
            "Schweißen": 0
        }
        vk0_doc_ref.set(vk0_data)
        st.success("'VK-0' document created successfully.")

        # Create Deckung document and add to Firebase
        deckung_doc_ref = db.collection(zeichnungs_nr).document('Deckung')
        deckung_data = {prop: 0 for prop in deckung_properties}
        deckung_doc_ref.set(deckung_data)
        st.success("'Deckung' document created successfully.")

        return True


def main():
    # Call get_session_state before any Streamlit function
    get_session_state()

    # Call login_app after get_session_state
    login_app()

    # Handle navigation or display other pages based on authentication status
    if st.session_state.authenticated:
        # Redirect to "Project Instantiation" page
        st.markdown("[Redirecting to Project Instantiation](https://ata-app-navigator.streamlit.app/)")
        key_dict = st.secrets["textkey"]
        creds = service_account.Credentials.from_service_account_info(key_dict)
        db = firestore.Client(credentials=creds)
        customer_list = fetch_customers(db)
        st.title('ATA App Navigator')
        image = Image.open('logo_ata.png')
        st.image(image, caption='Ata Logo')

        st.header('Project Instantiation')
        with st.form(key='project_form'):
            kunde = st.selectbox('Kunde', customer_list)
            benennung = st.text_input('Benennung')
            zeichnungs_nr = st.text_input('Zeichnungs Nr')
            ausfuehren_nr = st.text_input('Ausführen Nr')
            submit_button = st.form_submit_button(label='Create Project')

            if submit_button:
                success = instantiate_project(kunde, benennung, zeichnungs_nr, ausfuehren_nr, db)
                if success:
                    st.success('Project Created Successfully!')
                else:
                    st.error('A project with this Zeichnungs Nr already exists.')


if __name__ == "__main__":
    main()
