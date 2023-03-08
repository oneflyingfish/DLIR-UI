import streamlit as st
import time


st.set_page_config(page_title="DLIR-Allocator management")

x=st.empty()

for i in range(100):
    time.sleep(1)
    x.text(i)