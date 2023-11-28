import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os


# Navigation bar
def navigation_bar():
    apps = {
        "Project Instantiation": "https://ata-app-navigator.streamlit.app/",
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",
        "ATA-Dashboard-App": "https://ata-dashboard-app.streamlit.app/"
    }

    st.sidebar.title('Navigation')

    for app_name, app_url in apps.items():
        st.sidebar.markdown(f"[{app_name}]({app_url})")


navigation_bar()
st.title("Login Page")
