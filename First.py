import streamlit as st
import time

image_list = ["1.jpg", "2.jpg", "3.jpg"]

interval = 2

container = st.container()

# Loop through the images
for i in range(len(image_list)):
    container.image(image_list[i], caption=f"Image {i + 1}", use_column_width=True)

    time.sleep(interval)
