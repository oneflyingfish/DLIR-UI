import sys
import streamlit as st
import json
import account,home

def main():
    if "route" not in st.session_state:
        st.session_state["route"]="login"

    if st.session_state["route"]=="login":
        st.set_page_config(page_title="登录")
        account.LoginPage()
    elif st.session_state["route"]=="register":
        st.set_page_config(page_title="添加新用户")
        account.RegisterPage()
    elif st.session_state["route"]=="change_password":
        st.set_page_config(page_title="修改密码")
        account.ChangePasswordPage()
    elif st.session_state["route"]=="home":
        st.set_page_config(page_title="DLIR-Allocator管理后台")
        home.Home()
    

if __name__ == "__main__":
    main()