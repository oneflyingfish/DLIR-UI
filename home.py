import streamlit as st
import pandas as pd
import database
import account
import home_account,home_files,home_analyze,home_system

def Home():
    # 账户管理
    with st.sidebar.container():
        cols=st.columns([1,2,1])
        cols[1].image("img/manager.png",use_column_width=True)
        st.header("管理选项")
        account_select = st.selectbox("账户管理", ["隐藏","当前用户","查看所有账户","修改密码", "添加新用户", "退出登录"],index=1)
    if account_select == "隐藏":
        pass
    elif account_select=="当前用户":
        home_account.ShowCurrentAccount()
    elif account_select == "查看所有账户":
        home_account.ShowAccounts()
    elif account_select == "修改密码":
        account.ChangePasswordPage()
    elif account_select == "添加新用户":
        account.RegisterPage()
    elif account_select=="退出登录":
        st.session_state["route"]="login"
        del st.session_state["user_id"]
        st.experimental_rerun()

    # 文件管理
    with st.sidebar.container():
        file_select=st.selectbox("模型管理",["隐藏","查看所有模型","上传模型","删除模型"], index=0)

    if file_select=="隐藏":
        pass
    elif file_select=="查看所有模型":
        home_files.ViewModels()
    elif file_select=="上传模型":
        home_files.UploadModels()
    elif file_select=="删除模型":
        home_files.DeleteModels()
    
    # 模型分析
    with st.sidebar.container():
        model_select=st.selectbox("模型分析",["隐藏","模型信息","性能数据","子模型分析"], index=0)

    if model_select=="隐藏":
        pass
    elif model_select=="模型信息":
        home_analyze.DisplayModelInfo()
    elif model_select=="性能数据":
        home_analyze.TestModelPerformance()
    elif model_select=="子模型分析":
        home_analyze.ChildModelSplit()

    # 系统控制
    with st.sidebar.container():
        model_select=st.selectbox("系统控制",["隐藏","状态查询","系统监控", "调用接口信息"], index=0)

    if model_select=="隐藏":
        pass
    elif model_select=="状态查询":
        home_system.ControlSystem()
    elif model_select=="运行日志解析":
        pass
    elif model_select=="调用接口信息":
        home_system.ShowInterface()
