import streamlit as st
import time
import numpy as np

progress_bar = st.progress(0) # 显示进度条
status_text = st.empty() # 创建空占位符

for i in range(10):
    # 更新进度条值
    progress_bar.progress(i+1)
    # 更新占位符中的文本
    status_text.text(f'Processing data point {i+1}...')
    time.sleep(1)

# 清空显示
progress_bar.empty()
status_text.empty()