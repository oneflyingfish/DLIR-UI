import streamlit as st
import pandas as pd
import database
import account
from io import BytesIO
import datetime
import os

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

def ManageModels():
    st.markdown("#### 已缓存模型管理：")
    # 创建一个空数据帧，稍后将用于存储上传的数据
    data = BytesIO()
    # 创建一个文件上传组件，允许上传CSV文件
    uploaded_file = st.file_uploader("上传ONNX模型", type=["onnx"])

    new_filename=None
    usersDatabase=database.ReadUsersDatabase()

    # 如果用户上传了文件，将其读入数据帧中
    if uploaded_file is not None:
        data.write(uploaded_file.read())
        new_filename = st.text_input("请输入模型名称：",placeholder="不包含后缀")
        new_filename=new_filename.replace(" ","-")

        if new_filename is not None and len(new_filename)>0:
            os.makedirs(os.path.join(usersDatabase["system_path"],"Onnxs",new_filename),exist_ok=True)
            new_file_path = os.path.join(usersDatabase["system_path"],"Onnxs",new_filename, new_filename+".onnx")
            with open(new_file_path, "wb") as f:
                f.write(data.getbuffer())

            usersDatabase["models"][new_filename]={
                "name": new_filename, 
                "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "by_user": usersDatabase["users"][str(st.session_state["user_id"])]["username"],
                "path": new_file_path
            }
            database.WriteUsersDatabase(usersDatabase)

            st.success("文件已保存为: {}".format(new_file_path))    

    models={"模型名称":[],"上传日期":[],"创建者":[],"缓存路径":[]}
    for name in usersDatabase["models"]:
        models["模型名称"].append(usersDatabase["models"][name]["name"] if "name" in usersDatabase["models"][name] else "")
        models["创建者"].append(usersDatabase["models"][name]["by_user"] if "by_user" in usersDatabase["models"][name] else "")
        models["上传日期"].append(usersDatabase["models"][name]["date"] if "date" in usersDatabase["models"][name] else "")
        models["缓存路径"].append(usersDatabase["models"][name]["path"] if "path" in usersDatabase["models"][name] else "")

    st.dataframe(pd.DataFrame(models),use_container_width=True)

def Home():
    usersDatabase=database.ReadUsersDatabase()

    with st.sidebar.container():
        st.header("管理DLIR-Allocator")
        account_select = st.selectbox("账户管理", ["默认","当前用户","查看所有账户","修改密码", "添加新用户", "退出登录"],index=1)
    if account_select == "默认":
        pass
    elif account_select=="当前用户":
        ShowCurrentAccount()
    elif account_select == "查看所有账户":
        ShowAccounts()
    elif account_select == "修改密码":
        account.ChangePasswordPage()
    elif account_select == "添加新用户":
        account.RegisterPage()
    elif account_select=="退出登录":
        st.session_state["route"]="login"
        del st.session_state["user_id"]
        st.experimental_rerun()

    with st.sidebar.container():
        models_select=st.selectbox("模型管理",["隐藏","模型管理","模型分析"], index=0)

    if models_select=="隐藏":
        pass
    elif models_select=="模型管理":
        ManageModels()
    
    
