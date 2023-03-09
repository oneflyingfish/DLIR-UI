import sys
import streamlit as st
import json
import account,home

def main():

    if "route" not in st.session_state:
        st.session_state["route"]="login"

    if st.session_state["route"]=="login":
        st.set_page_config(page_title="登录",page_icon="🧊")
        account.LoginPage()
    elif st.session_state["route"]=="home":
        st.set_page_config(page_title="DLIR-Allocator管理后台",page_icon="🧊",layout="wide")
        home.Home()
    

if __name__ == "__main__":
    st.set_option("deprecation.showfileUploaderEncoding", False)
    main()