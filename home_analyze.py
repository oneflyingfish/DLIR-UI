import streamlit as st
import pandas as pd
import database
import os
import json,time
import matplotlib.pyplot as plt
import numpy as np

def InsertIOLine(table_datas: dict, data)->dict:
    if "输入名称" not in table_datas:
        table_datas["变量名称"]=[]
    if "数据类型" not in table_datas:
        table_datas["数据类型"]=[]
    if "数据规模" not in table_datas:
        table_datas["数据规模"]=[]

    print(data)
    for value in data["data"]:
        table_datas["变量名称"].append(value["name"])
        table_datas["数据类型"].append(value["type"])
        table_datas["数据规模"].append("×".join([str(i) for i in value["shape"]]))
    
    return table_datas

def ShowModelIOInfo(info_json,name):
    st.markdown("###### {}:".format(name))
    cols = st.columns([6,1,6])

    cols[0].text("输入数据:")
    cols[0].dataframe(pd.DataFrame(InsertIOLine({},info_json["input"])),use_container_width=True)
    cols[2].text("输出数据:")
    cols[2].dataframe(pd.DataFrame(InsertIOLine({},info_json["output"])),use_container_width=True)

def DisplayModelInfo():
    st.markdown("#### 原模型信息:")
    models=database.ReadUsersDatabase()["models"]

    for name in models:
        if os.path.exists(os.path.join(models[name]["fold"],name+".json")):
            # read-log
            with open(os.path.join(models[name]["fold"],name+".json"),"r") as fp:
                ShowModelIOInfo(json.load(fp),name)
        else:
            # run analyze
            pass

def TestModelPerformance():
    st.markdown("#### 性能测试数据:")
    models=database.ReadUsersDatabase()["models"]

    st.markdown("###### 测试:")
    if not os.path.exists(os.path.join(os.getcwd(),"logs/test_model_latency.json")):
        # run
        pass

    with open(os.path.join(os.getcwd(),"logs/test_model_latency.json"),"r") as fp:
        latencys=json.load(fp)

        process_cols=st.columns(5)

        model_index=0
        for name in models:
            x_label="{}-测试次数".format(name)
            y_label="延迟（ms）"
            data={x_label:[],y_label:[]}
            chart = process_cols[model_index%5].line_chart(pd.DataFrame(data),use_container_width=True, x=x_label, y=y_label)

            for latency in latencys[name]:
                # 生成新数据点
                time.sleep(latency/1000.0)
                data[x_label].append(len(data[x_label])+1)
                data[y_label].append(latency)

                chart.line_chart(pd.DataFrame(data),use_container_width=True, x=x_label, y=y_label)

            # 绘制下一个模型
            model_index+=1

    st.markdown("###### 结论:")
    result_cols=st.columns([2,3,2,3,2])

    # 绘制原模型柱状图
    if not os.path.exists(os.path.join(os.getcwd(),"logs/test_model_latency.json")):
        # run
        pass
    
    with open(os.path.join(os.getcwd(),"logs/test_result_latency.json"),"r") as fp:
        avg_latencys=json.load(fp)


    avg_x=[]
    avg_y=[]
    for name in models:
        avg_x.append(name)
        avg_y.append(avg_latencys[name])
    

    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 13
    fig, ax = plt.subplots()
    ax.bar(avg_x,avg_y,color=['r', 'g', 'orange', 'c', 'y'])
    ax.set_xlabel('（原始模型）')
    ax.set_ylabel('推理延迟（ms）')

    # 显示图形
    result_cols[1].pyplot(fig)

    # 最优子模型
    if not os.path.exists(os.path.join(os.getcwd(),"logs/test_model_latency.json")):
        # run
        pass
    
    with open(os.path.join(os.getcwd(),"logs/test_result_latency_best.json"),"r") as fp:
        avg_latencys_c=json.load(fp)

    avg_x_c=[]
    avg_y_c=[]
    for name in models:
        avg_x_c.append(name)
        avg_y_c.append(avg_latencys_c[name])
    
    fig_c, ax_c = plt.subplots()
    ax_c.bar(avg_x_c,avg_y_c,color=['r', 'g', 'orange', 'c', 'y'])
    ax_c.set_xlabel('（理想状态下最优子模型方案）')
    ax_c.set_ylabel('推理延迟（ms）')

    # 显示图形
    result_cols[3].pyplot(fig_c)

    # 绘制表格
    if not os.path.exists(os.path.join(os.getcwd(),"logs/test_result_table.json")):
        # run
        pass

    with open(os.path.join(os.getcwd(),"logs/test_result_table.json"),"r") as fp:
        evaluate_latencys=json.load(fp)

        indexs=[]
        for i in range(len(evaluate_latencys["模型名称"])):
            if evaluate_latencys["模型名称"][i] in models:
                indexs.append(i)

        show_evaluate_latencys={}
        for key in evaluate_latencys:
            show_evaluate_latencys[key] = [evaluate_latencys[key][i] for i in indexs]

        st.dataframe(pd.DataFrame(show_evaluate_latencys),use_container_width=True)

def ShowModelSplit(name,count,json_log):
    st.markdown("###### {} (子模型数量={}):".format(name,str(count)))
    
    cols = st.columns([3,3,3])

    latency_data=[]
    for _ in range(count):
        latency_data.append([])
    overhead_data=[]
    std_data=[]
    iter_data=[]

    cols[0].text("子模型延迟变化（ms）:")
    tmp={"子模型-"+str(i+1): latency_data[i] for i in range(len(latency_data))}
    tmp["迭代次数"]=iter_data
    chart_latency = cols[0].line_chart(pd.DataFrame(tmp),use_container_width=True, x="迭代次数")

    cols[1].text("开销变化:")
    chart_overhead=cols[1].line_chart(pd.DataFrame({"开销": overhead_data, "迭代次数": iter_data}),use_container_width=True, x="迭代次数")
    cols[2].text("标准差:")
    chart_std=cols[2].line_chart(pd.DataFrame({"标准差": std_data, "迭代次数": iter_data}),use_container_width=True, x="迭代次数")

    for iter in range(1,int(json_log["iter_count"])+1):
        iter_data.append(iter)
        for index in range(len(json_log[str(iter)]["costs"])):
            latency_data[index].append(json_log[str(iter)]["costs"][index])
        overhead_data.append(json_log[str(iter)]["overhead"])
        std_data.append(json_log[str(iter)]["std"])

        chart_latency.line_chart(pd.DataFrame(tmp),use_container_width=True, x="迭代次数")
        chart_overhead.line_chart(pd.DataFrame({"开销": overhead_data, "迭代次数": iter_data}),use_container_width=True, x="迭代次数")
        chart_std.line_chart(pd.DataFrame({"标准差": std_data, "迭代次数": iter_data}),use_container_width=True, x="迭代次数")
        time.sleep(0.2)
    
def ChildModelSplit():
    st.markdown("#### 模型切分分析:")
    models=database.ReadUsersDatabase()["models"]

    st.markdown("###### 测试:")
    if not os.path.exists(os.path.join(os.getcwd(),"logs/split-log.json")):
        # run
        pass

    with open(os.path.join(os.getcwd(),"logs/split-log.json"),"r") as fp:
        latencys=json.load(fp)

    # 获取要绘制的模型
    analyze_models=[]
    for model in latencys:
        if model in models:
            analyze_models.append(model)

    model_names=[]
    model_counts=[]
    model_overhead=[]
    model_range=[]
    model_range_percent=[]
    for model_name in analyze_models:
        counts=sorted([int(count) for count in latencys[model_name]])
        for count in counts:
            ShowModelSplit(model_name,count,latencys[model_name][str(count)])
            model_names.append(model_name)
            model_counts.append(str(count))
            best=latencys[model_name][str(count)][str(latencys[model_name][str(count)]["iter_count"])]
            model_overhead.append('{:.2%}'.format(best["overhead"]))
            model_range.append(str(max(best["costs"])-min(best["costs"])))
            model_range_percent.append('{:.2%}'.format((max(best["costs"])-min(best["costs"]))*(1.0+best["overhead"])/sum(best["costs"])))
    
    st.table(pd.DataFrame({"模型名称":model_names,"子模型数量": model_counts, "切分开销": model_overhead,"极差（ms）": model_range,"极差/原模型推理延迟":model_range_percent}))

    st.session_state["vgg19"]=3
    st.session_state["resnet50"]=2