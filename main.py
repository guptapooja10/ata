import streamlit as st
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
from Deckung import deckung_properties

# Initialize session state data if it doesn't exist
if 'main_data' not in st.session_state:
    st.session_state.main_data = {}


# Function to instantiate a new project and save it to Firestore
def instantiate_project(kunde, benennung, zeichnungs_nr, ausfuehren_nr, db):
    doc_ref = db.collection(zeichnungs_nr).document('Details')
    doc = doc_ref.get()
    if doc.exists:
        print(f"A project with Zeichnungs Nr {zeichnungs_nr} already exists.")
        return False
    else:
        project_data = {
            "Kunde": kunde,
            "Benennung": benennung,
            "Ausführen Nr": ausfuehren_nr,
            "Zeichnungs- Nr.": zeichnungs_nr
        }
        doc_ref.set(project_data)
        print(f"Project with Zeichnungs Nr {zeichnungs_nr} created successfully.")

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
    key_dict = st.secrets["textkey"]
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds)
    st.title('ATA App Navigator')
    image = Image.open('logo_ata.png')
    st.image(image, caption='Ata Logo')
    apps = {
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",
        "ATA-Dashboard-App": "https://ata-dashboard-app.streamlit.app/"
    }

    st.sidebar.title('Navigation')

    for app_name, app_url in apps.items():
        st.sidebar.markdown(f"[{app_name}]({app_url})")

    st.header('Project Instantiation')
    # Input fields for project instantiation
    with st.form(key='project_form'):
        kunde = st.text_input('Kunde')
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
