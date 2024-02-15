import streamlit as st
import numpy as np
from PIL import Image

@st.cache_data
def get_images():
    image_paths = [
        "1.jpg",
        "2.jpg",
        "3.jpg",
    ]

    images = [Image.open(image_path) for image_path in image_paths]
    return images

tabs = st.tabs(list(np.array(range(1, 4)).astype(str)))

images = get_images()

for i in range(len(images)):
    # Display an image in each tab
    tabs[i].image(images[i], caption=f"Image {i + 1}")
