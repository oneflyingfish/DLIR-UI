from io import BytesIO
import streamlit as st
import pandas as pd
import database
from io import BytesIO
import datetime
import os
import shutil

def UploadModels():
    st.markdown("#### 上传模型：")
    # 创建一个空数据帧，稍后将用于存储上传的数据
    data = BytesIO()
    # 创建一个文件上传组件，允许上传CSV文件
    uploaded_file = st.file_uploader("上传ONNX模型", type=["onnx"])

    new_filename=None
    usersDatabase=database.ReadUsersDatabase()

    # 如果用户上传了文件，将其读入数据帧中
    if uploaded_file is not None:
        data.write(uploaded_file.read())
        new_filename = st.text_input("请输入模型名称：",placeholder="不包含后缀",max_chars=10,value=uploaded_file.name.rstrip(".onnx"))
        new_filename=new_filename.replace(" ","-")

        if st.button("确认提交"):
            if new_filename is not None and len(new_filename)>0:
                os.makedirs(os.path.join(usersDatabase["system_path"],"Onnxs",new_filename),exist_ok=True)
                new_file_path = os.path.join(usersDatabase["system_path"],"Onnxs",new_filename, new_filename+".onnx")
                with open(new_file_path, "wb", encoding='utf-8') as f:
                    f.write(data.getbuffer())

                usersDatabase["models"][new_filename]={
                    "name": new_filename, 
                    "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "by_user": usersDatabase["users"][str(st.session_state["user_id"])]["username"],
                    "fold": os.path.join(usersDatabase["system_path"],"Onnxs",new_filename),
                    "path": new_file_path
                }
                database.WriteUsersDatabase(usersDatabase)

                st.success("文件已保存为: {}".format(new_file_path))    
            else:
                st.error("命名不符合规范")

    models={"模型名称":[],"上传日期":[],"创建者":[],"缓存路径":[]}
    for name in usersDatabase["models"]:
        models["模型名称"].append(usersDatabase["models"][name]["name"] if "name" in usersDatabase["models"][name] else "")
        models["创建者"].append(usersDatabase["models"][name]["by_user"] if "by_user" in usersDatabase["models"][name] else "")
        models["上传日期"].append(usersDatabase["models"][name]["date"] if "date" in usersDatabase["models"][name] else "")
        models["缓存路径"].append(usersDatabase["models"][name]["path"] if "path" in usersDatabase["models"][name] else "")

    st.dataframe(pd.DataFrame(models),use_container_width=True)

def DeleteModels():
    st.markdown("#### 删除模型：")
    usersDatabase=database.ReadUsersDatabase()
    models={"模型名称":[],"上传日期":[],"创建者":[],"缓存路径":[]}
    for name in usersDatabase["models"]:
        models["模型名称"].append(usersDatabase["models"][name]["name"] if "name" in usersDatabase["models"][name] else "")
        models["创建者"].append(usersDatabase["models"][name]["by_user"] if "by_user" in usersDatabase["models"][name] else "")
        models["上传日期"].append(usersDatabase["models"][name]["date"] if "date" in usersDatabase["models"][name] else "")
        models["缓存路径"].append(usersDatabase["models"][name]["path"] if "path" in usersDatabase["models"][name] else "")

    table=pd.DataFrame(models)

    # 创建一个复选框，允许用户选择要删除的行
    x = st.empty()
    rows_to_delete = x.multiselect("选择要删除的行", table.index.tolist())

    # 如果用户选择了行，请从数据帧中删除它们
    if len(rows_to_delete) > 0:
        table = table.drop(rows_to_delete)
    
    delete_modes=[models["模型名称"][i] for i in rows_to_delete if models["模型名称"][i] in usersDatabase["models"]]

    # 显示表格
    st.dataframe(table,use_container_width=True)
    
    if st.button("确认删除"):
        for name in delete_modes:
            if os.path.exists(usersDatabase["models"][name]["fold"]):
                shutil.rmtree(usersDatabase["models"][name]["fold"])
            del usersDatabase["models"][name]
            database.WriteUsersDatabase(usersDatabase)

        delete_modes=[]
    if len(delete_modes)>0:
        st.info("模型：{} 将被删除".format("、".join(delete_modes)))

def ViewModels():
    st.markdown("#### 所有模型：")
    usersDatabase=database.ReadUsersDatabase()
    models={"模型名称":[],"上传日期":[],"创建者":[],"缓存路径":[]}
    for name in usersDatabase["models"]:
        models["模型名称"].append(usersDatabase["models"][name]["name"] if "name" in usersDatabase["models"][name] else "")
        models["创建者"].append(usersDatabase["models"][name]["by_user"] if "by_user" in usersDatabase["models"][name] else "")
        models["上传日期"].append(usersDatabase["models"][name]["date"] if "date" in usersDatabase["models"][name] else "")
        models["缓存路径"].append(usersDatabase["models"][name]["path"] if "path" in usersDatabase["models"][name] else "")

    st.dataframe(pd.DataFrame(models),use_container_width=True)