import streamlit as st
import time

image_list = ["1.jpg", "2.jpg", "3.jpg"]

interval = 2

st.title("ATA")
for i in range(len(image_list)):
    st.image(image_list[i], caption=f"Image {i + 1}", use_column_width=True)

    time.sleep(interval)
