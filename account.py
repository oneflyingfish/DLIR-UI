import database
import streamlit as st
import time
import datetime

def RegisterPage():
    st.title("创建新用户")

    # 显示用户名和密码输入框
    newUsername = st.text_input("新用户名：",placeholder="请输入用户名")
    newPassword = st.text_input("新密码：", type="password",placeholder="请输入密码")
    newPasswordAgain = st.text_input("重复密码：", type="password",placeholder="请再次输入密码")

    createCol, homeCol = st.columns([1,1])

    st.markdown(
        """
        <style>
        .stButton button {
            width: 100%;
        }
        .button-row {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .createCol {
            width: 50%;
            display: flex;
            justify-content: flex-start;
        }
        .homeCol {
            width: 50%;
            display: flex;
            justify-content: flex-end;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if homeCol.button("退出重新登录"):
        st.session_state["route"]="login"
        del st.session_state["user_id"]
        st.experimental_rerun()

    # 当用户单击注册按钮时执行以下代码
    if createCol.button("创建"):
        if len(newPassword)<6:
            st.error("密码不得少于6位！")
            return
        elif newPasswordAgain !=newPassword:
            st.error("密码不一致！")
            return
        else:
            # 读取用户数据库
            usersDatabase = database.ReadUsersDatabase()

            # 检查新用户名是否已经存在
            for id_str in usersDatabase["users"]:
                if usersDatabase["users"][id_str]["username"] == newUsername:
                    st.error("用户已经存在！")
                    return

        # 为新用户创建唯一的ID
        if len(usersDatabase["users"])<1:
            newId=1
        else:
            newId = max([int(id_str) for id_str in usersDatabase["users"]]) + 1

        # 将新用户添加到用户数据库中
        newUser = {"id": newId, "username": newUsername, "password": newPassword, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "by_user": usersDatabase["users"][str(st.session_state["user_id"])]["username"]}
        usersDatabase["users"][newId]=newUser
        database.WriteUsersDatabase(usersDatabase)

        st.success("用户注册成功！")
    

def ChangePasswordPage():
    st.title("修改密码")

    # 密码输入框
    newPassword = st.text_input("新密码：", type="password",placeholder="请输入密码")
    newPasswordAgain = st.text_input("重复密码：", type="password",placeholder="请再次输入密码")

    createCol, homeCol = st.columns(2)

    st.markdown(
        """
        <style>
        .stButton button {
            width: 100%;
        }
        .button-row {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .createCol {
            width: 50%;
            display: flex-start;
            justify-content: flex-start;
        }
        .homeCol {
            width: 50%;
            display: flex-end;
            justify-content: flex-end;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 当用户单击注册按钮时执行以下代码
    if createCol.button("修改"):
        if len(newPassword)<6:
            st.error("密码不得少于6位！")
            return
        elif newPasswordAgain !=newPassword:
            st.error("密码不一致！")
            return
        elif "user_id" not in st.session_state:
            st.error("您尚未登录，将自动跳转到登录页面...")
            time.sleep(1)
            st.session_state["route"]="login"
            st.experimental_rerun()
        usersDatabase = database.ReadUsersDatabase()
        usersDatabase["users"][str(st.session_state["user_id"])]["password"]=newPassword
        database.WriteUsersDatabase(usersDatabase)

        st.success("密码修改成功, 即将转到登录页面...")
        time.sleep(1)

        st.session_state["route"]="login"
        del st.session_state["user_id"]
        st.experimental_rerun()

def LoginPage():
    usersDatabase = database.ReadUsersDatabase()
    if "user_id" in st.session_state and st.session_state["user_id"] in usersDatabase["users"]:
        st.session_state["route"]="home"
        st.experimental_rerun()

    st.title("登录")
    # 显示用户名和密码输入框
    username = st.text_input("用户名：",placeholder="请输入用户名")
    password = st.text_input("密码：", type="password",placeholder="请输入密码")
    loginCol, registerCol = st.columns(2)

    st.markdown(
        """
        <style>
        .stButton button {
            width: 100%;
        }
        .button-row {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .loginCol {
            width: 50%;
            display: flex-start;
            justify-content: flex-start;
        }
        .registerCol {
            width: 50%;
            display: flex-end;
            justify-content: flex-end;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 当用户单击登录按钮时执行以下代码
    if loginCol.button("登录"):
        # 遍历用户数据库，检查用户名和密码是否匹配
        for id_str in usersDatabase["users"]:
            if usersDatabase["users"][id_str]["username"] == username and usersDatabase["users"][id_str]["password"] == password:
                st.session_state["user_id"]=int(id_str)
                st.success("欢迎你, {}!   即将跳转至首页...".format(username))
                time.sleep(1)
                st.session_state["route"]="home"
                st.experimental_rerun()

        st.error("用户名或密码错误！")
    # if registerCol.button("添加新用户"):
    #     st.session_state["route"]="register"
    #     st.experimental_rerun()

    st.info("默认账户：见设备说明书！")