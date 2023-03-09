import streamlit as st
import pandas as pd

# 创建一个空数据帧，稍后将用于存储上传的数据
data = pd.DataFrame()

# 创建一个文件上传组件，允许上传CSV文件
uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])

# 如果用户上传了文件，将其读入数据帧中
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

# 显示数据帧的前五行
st.write(data.head())

# 创建一个复选框，允许用户选择要删除的行
rows_to_delete = st.multiselect("选择要删除的行", data.index.tolist())

# 如果用户选择了行，请从数据帧中删除它们
if len(rows_to_delete) > 0:
    data = data.drop(rows_to_delete)

# 显示更新后的数据帧
st.write(data)
