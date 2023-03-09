# DLIR-UI
UI for DLIR

# install

```shell
# install python3 before
pip3 install streamlit
```

# run

```shell
# windows
streamlit run main.py

# Linux
python3 -m streamlit run main.py --server.fileWatcherType poll
```


<!-- 
    # 创建一个空数据帧，稍后将用于存储上传的数据
    table = pd.DataFrame()
    data = BytesIO()

    # 创建一个文件上传组件，允许上传CSV文件
    uploaded_file = st.file_uploader("上传ONNX模型", type=["onnx"])

    # 如果用户上传了文件，将其读入数据帧中
    if uploaded_file is not None:
        table = pd.read_csv(uploaded_file)

    # 显示数据帧的前五行
    st.write(table.head())

    # 创建一个复选框，允许用户选择要删除的行
    rows_to_delete = st.multiselect("选择要删除的行", table.index.tolist())

    # 如果用户选择了行，请从数据帧中删除它们
    if len(rows_to_delete) > 0:
        table = table.drop(rows_to_delete)

    # 显示更新后的数据帧
    st.write(table) -->