import streamlit as st

# 创建一个容器并指定宽度
container = st.container()
container.width = 500

# 在容器中添加控件
with container:
    st.write("这是一个在框框里面的文本")
    value = st.slider("选择一个值", 0, 100, 50)
    st.write("您选择的值是：", value)