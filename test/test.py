import streamlit as st

# 登录页面
def login_page():
    st.title("登录页面")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        if username == "admin" and password == "admin":
            # 跳转到主页面
            main_page()
        else:
            st.error("用户名或密码错误")

# 主页面
def main_page():
    st.title("主页面")
    st.write("欢迎登录！")
    if st.button("退出登录"):
        # 跳转回登录页面
        login_page()

# 默认显示登录页面
login_page()
