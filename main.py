import streamlit as st
from PIL import Image


def main():
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


if __name__ == "__main__":
    main()
