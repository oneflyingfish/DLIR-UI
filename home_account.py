import streamlit as st
import pandas as pd
import database


def ShowAccounts():
    usersDatabase=database.ReadUsersDatabase()
    st.markdown("#### 所有账户:")
    users={"用户名":[],"注册日期":[],"账户创建者":[]}
    for id_str in usersDatabase["users"]:
        users["用户名"].append(usersDatabase["users"][id_str]["username"] if "username" in usersDatabase["users"][id_str] else "")
        users["注册日期"].append(usersDatabase["users"][id_str]["date"] if "date" in usersDatabase["users"][id_str] else "")
        users["账户创建者"].append(usersDatabase["users"][id_str]["by_user"] if "by_user" in usersDatabase["users"][id_str] else "")

    st.dataframe(pd.DataFrame(users),use_container_width=True)

def ShowCurrentAccount():
    usersDatabase=database.ReadUsersDatabase()
    st.header("{}, 欢迎你!".format(usersDatabase["users"][str(st.session_state["user_id"])]["username"]))