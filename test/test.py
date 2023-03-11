import streamlit as st
import plotly.express as px

# 定义扇形图数据
data = dict(
    values=[15, 30, 45, 10],
    labels=['A', 'B', 'C', 'D'],
    title='Pie Chart'
)

# 绘制扇形图
fig = px.pie(data, values='values', names='labels', title='Pie Chart')

# 显示图表
st.plotly_chart(fig)