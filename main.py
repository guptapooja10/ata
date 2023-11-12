import streamlit as st
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import json


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
        return True


def main():
    # Authenticate to Firestore with the JSON account key.
    # db = firestore.Client.from_service_account_json(
    # "anlagentechnik-aschersleben-firebase-adminsdk-sfoug-5eb13936b2.json")
    with open('anlagentechnik-aschersleben-firebase-adminsdk-sfoug-5eb13936b2.json', 'r') as key_file:
        key_dict = json.load(key_file)

    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds)


    # key_dict = st.secrets["textkey"]
    # creds = service_account.Credentials.from_service_account_info(key_dict)
    # db = firestore.Client(credentials=creds)
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
