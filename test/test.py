import streamlit as st
import matplotlib.pyplot as plt

# 数据
data = [20, 30, 25, 35, 27]

# 创建条状图
fig, ax = plt.subplots()
ax.bar(range(len(data)), data)

# 添加坐标轴标签
ax.set_xlabel('X轴标签')
ax.set_ylabel('Y轴标签')

# 显示图形
st.pyplot(fig)
