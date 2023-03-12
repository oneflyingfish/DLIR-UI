import streamlit as st
import os,datetime,time,random,json
import database
import copy
import pandas as pd
import socket
from typing import Tuple,Dict,List
import matplotlib.pyplot as plt
from collections import deque

MAX_DATA=2000
MAX_RR_DATA=2000

def DealTime(value:int)->int:
    return value//1000  # us to ms

def AddtoList(datas:List[List[deque]],value:tuple)->List[list]:
    if len(datas)<2 or len(datas[1])<2:
        datas[0].append(value[0])
        datas[1].append(value[1])
        return datas
    
    if datas[1][-1]==value[1] and datas[1][-2]==value[1]:
        datas[0].pop()
        datas[1].pop()

    datas[0].append(value[0])
    datas[1].append(value[1])
    return datas


def FlushDatas(current_time:int,times_serial:list,resour_time:List[List[deque]],tasks_time:Dict[str,List[List[deque]]],RR_time:dict,task_start_ends_tmp:dict,resource_uses_tmp:list,RR_logs_tmp:list,model_dict:dict)->Tuple[list,list,dict,dict]:
    # 更新时间序列
    times_serial.append(current_time)

    # 更新资源序列
    while True:
        if len(resource_uses_tmp)<1:
            # 没有任务继续使用资源了
            resour_time=AddtoList(resour_time,(current_time,model_dict["等待任务"]))
            break

        related=resource_uses_tmp[-1]
        if current_time<related[0]:
            resour_time=AddtoList(resour_time,(current_time,model_dict["等待任务"]))
            break
        elif current_time>=related[0] and current_time<=related[1]:
            resour_time=AddtoList(resour_time,(current_time,model_dict[related[2]]))
            break
        else:
            # 当前加载子任务已经被处理完毕
            resource_uses_tmp.pop()
            continue
    
    # 更新任务数量序列
    total_count=0
    for model_name,count_list in tasks_time.items():
        if model_name=="total":
            continue
        current_count=count_list[1][-1]
        # 增加任务
        while True:
            if len(task_start_ends_tmp[model_name]["recv"])<1:
                # 不会有任务到达了
                break

            if task_start_ends_tmp[model_name]["recv"][-1]<current_time:
                task_start_ends_tmp[model_name]["recv"].pop()
                continue
            elif task_start_ends_tmp[model_name]["recv"][-1]==current_time:
                current_count+=1
                task_start_ends_tmp[model_name]["recv"].pop()
                continue
            else:
                # 下一个最近任务尚未到达
                break
        
        # 完成任务
        while True:
            if len(task_start_ends_tmp[model_name]["end"])<1:
                # 不会有任务到达了
                break

            if task_start_ends_tmp[model_name]["end"][-1]<current_time:
                task_start_ends_tmp[model_name]["end"].pop()
                continue
            elif task_start_ends_tmp[model_name]["end"][-1]==current_time:
                current_count-=1
                task_start_ends_tmp[model_name]["end"].pop()
                continue
            else:
                # 下一个最近完成任务时刻尚未到达
                break
        tasks_time[model_name]=AddtoList(tasks_time[model_name],(current_time,current_count))
        total_count+=current_count
    tasks_time["total"]=AddtoList(tasks_time["total"],(current_time,total_count))
    # tasks_time["total"].append(total_count)

    ## 更新响应比
    update={}
    for k in RR_time["models"]+["total"]:
        update[k]=[0,0]

    while True:
        if len(RR_logs_tmp)<1:
            # 响应比没变化
            break
        related=RR_logs_tmp[-1]
        if current_time<related[0]:
            # 响应比没变化
            break
        elif current_time>=related[0] and current_time<=related[0]:
            update[related[2]][0]+=related[1]
            update[related[2]][1]+=1
            update["total"][0]+=related[1]
            update["total"][1]+=1
            break
        else:
            # 当前加载子任务已经被处理完毕
            RR_logs_tmp.pop()
            continue
    
    new_data={}
    for model_name,con in update.items():
        relate=RR_time[model_name][-1]
        new_data[model_name]=(relate[0]+con[0],relate[1]+con[1],((relate[0]+con[0])/(relate[1]+con[1])) if (relate[1]+con[1])>0 else 1)
        # RR_time[model_name].append(new_data[model_name])
    # RR_time["times"].append(current_time)
    RR_time=AddToRRDict(RR_time,new_data,current_time)

    return times_serial,resour_time,tasks_time,RR_time

def AddToRRDict(datas,new_data:dict,current_time:int):
    if "times" not in datas or len(datas["times"])<2:
        for model_name in new_data:
            datas[model_name].append(new_data[model_name])
        datas["times"].append(current_time)
        return datas
    
    flag=True   # 可以缩减
    for model_name,new_value in new_data.items():
        if datas[model_name][-1]!=new_value or datas[model_name][-2]!=new_value:
            flag=False
            break
    
    if flag:
        for model_name in new_data:
            datas[model_name].pop()
        datas["times"].pop()
    
    for model_name in new_data:
        datas[model_name].append(new_data[model_name])
    datas["times"].append(current_time)
    return datas
    

def AnalyzeLogs()->Tuple[list,dict,list]:
    files=[file_name for file_name in os.listdir(os.path.join(os.getcwd(),"logs/tasks_log")) if file_name.endswith(".json")]
    resource_uses=[]
    task_start_ends={}
    RR=[]

    for log_file in files:
        with open(os.path.join(os.getcwd(),"logs/tasks_log",log_file),"r", encoding='utf-8') as fp:
            tmp_data=json.load(fp)
            model_name=tmp_data["model_name"]
            if model_name not in task_start_ends:
                task_start_ends[model_name]=[]
            task_start_ends[model_name].append((DealTime(tmp_data["recv_time"]),DealTime(tmp_data["finish_time"])))
            
            for child_info in tmp_data["child_model_run_time"]:
                resource_uses.append((DealTime(child_info[0]),DealTime(child_info[1]),model_name))
            
            rr_tmp=max(1.0,tmp_data["total_cost_by_ms"]/tmp_data["limit_cost_by_ms"])
            RR.append((DealTime(tmp_data["finish_time"]),rr_tmp,model_name))
    resource_uses=sorted(resource_uses,key=lambda x:x[0])

    for model_name in task_start_ends:
        task_start_ends[model_name]=sorted(task_start_ends[model_name],key=lambda x:x[0])

    # RR：[(当前总响应比加和，任务数量),...]
    return resource_uses,task_start_ends,sorted(RR,key=lambda x:x[0])

# def DrawTotal(RR:dict,RR_chart,fig,ax):
#     # ax.clear()
#     x=[]
#     y=[]
#     for k,v in RR.items():
#         x.append(k)
#         y.append(v[0]/v[1] if v[1]>0 else 1)
#     ax.bar(x,y,color=['r', 'g', 'orange', 'c', 'y','blue'][:len(RR)])
#     ax.set_ylabel('平均响应比')

#     print(RR)
#     # 显示图形
#     RR_chart.pyplot(fig)


def delay_1ms():
    time.sleep(0.0001)

def RunTimeLog():
    st.markdown("#### 系统监控日志：")

    # 求解任务情况
    resource_uses,task_start_ends,RR_logs = AnalyzeLogs()
    task_start_ends_tmp={}
    max_time=0
    min_time=float("inf")
    for model_name in task_start_ends:
        task_start_ends_tmp[model_name]={}
        task_start_ends_tmp[model_name]["recv"]=sorted([v[0] for v in task_start_ends[model_name]],reverse=True)
        task_start_ends_tmp[model_name]["end"]=sorted([v[1] for v in task_start_ends[model_name]],reverse=True)
        max_time=max(max_time,task_start_ends_tmp[model_name]["end"][0])
        min_time=min(min_time,task_start_ends_tmp[model_name]["recv"][-1])
    min_time=max(min_time-10,0)
    resource_uses_tmp=copy.deepcopy(resource_uses[::-1])
    RR_logs_tmp = copy.deepcopy(RR_logs[::-1])

    times_serial=[min_time]                 # [17701,17702,17703,...]
    tasks_time={"total":[deque([min_time],maxlen=MAX_DATA),deque([0],maxlen=MAX_DATA)]}                # {"total": [...], "vgg19":[...]}，存储为某时刻任务数量
    RR_time={"total":deque([(0,0,1)],maxlen=MAX_RR_DATA),"times":deque([min_time],maxlen=MAX_RR_DATA),"models":[]}             # {"total": [...], "vgg19":[...]}, 存储为[(当前总响应比加和，任务数量，平均响应比)]
    
    for model_name in task_start_ends:
        tasks_time[model_name]=[deque([min_time],maxlen=MAX_DATA),deque([0],maxlen=MAX_DATA)]
        RR_time["models"].append(model_name)
        RR_time[model_name]=deque([(0,0,1)],maxlen=MAX_RR_DATA)
    resour_time=[deque([min_time],maxlen=MAX_DATA),deque([0],maxlen=MAX_DATA)]                         # [0,1,2,1,3,5]，数字表示某时刻资源占用类型

    st.markdown("##### 任务数量：")
    tmp={"时间（ms）": times_serial}
    count_charts={}

    # 分列展示
    # count_cols = st.columns(5)
    # start_index=0
    # for model_name in task_start_ends:
    #     # tmp[model_name]=tasks_time[model_name]
    #     count_cols[start_index%5].markdown("###### {}：".format(model_name))
    #     count_charts[model_name]=count_cols[start_index%5].line_chart(pd.DataFrame({"时间（ms）": times_serial, "排队任务数量":tasks_time[model_name]}),use_container_width=True, x="时间（ms）")
    #     start_index+=1

    # 伸缩框展示
    for model_name in task_start_ends:
        # tmp[model_name]=tasks_time[model_name]
        expander = st.expander("展示{}:".format(model_name))
        expander.markdown("###### {}：".format(model_name))
        count_charts[model_name]=expander.line_chart(pd.DataFrame({"时间（ms）": tasks_time[model_name][0], "排队任务数量":tasks_time[model_name][1]}),use_container_width=True, x="时间（ms）")
    expander_total = st.expander("展示{}:".format("total"))
    expander_total.markdown("###### {}：".format("total"))
    count_charts["total"]=expander_total.line_chart(pd.DataFrame({"时间（ms）": tasks_time["total"][0], "排队任务数量":tasks_time["total"][1]}),use_container_width=True, x="时间（ms）")

    st.markdown("##### 资源占用：")
    model_keys=["等待任务"]+list(task_start_ends.keys())+["未知"]
    model_dict={model_keys[i]: i for i in range(len(model_keys))}

    # 显示表格
    table_data={"资源占用类型":["编号"]}
    for key,value in model_dict.items():
        table_data[key]=[str(value)]
    st.table(table_data)

    resource_chart=st.line_chart(pd.DataFrame({"时间（ms）": resour_time[0],"资源占用类型":resour_time[1]}),use_container_width=True, x="时间（ms）")


    st.markdown("##### 平均响应比分析：")
    # RR_cols=st.columns([1,2,1])
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # plt.rcParams['font.size'] = 13
    # fig, ax = plt.subplots()
    # x=[]
    # y=[]
    # for k,v in RR_time.items():
    #     x.append(k)
    #     y.append(v[0]/v[1] if v[1]>0 else 1)
    # ax.bar(x,y,color=['r', 'g', 'orange', 'c', 'y','blue'][:len(RR_time)])
    # ax.set_ylabel('平均响应比')

    # # 显示图形
    # RR_chart=RR_cols[1].pyplot(fig)
    tmp={"时间（ms）": RR_time["times"]}
    for model_name in RR_time["models"]+["total"]:
        tmp[model_name]=[v[2] for v in RR_time[model_name]]
    RR_chart=st.line_chart(pd.DataFrame(tmp),use_container_width=True, x="时间（ms）")

    if max_time>min_time:
        for current_time in range(min_time+1,max_time+1):
            delay_1ms()
            times_serial,resour_time,tasks_time,RR_time=FlushDatas(current_time,times_serial,resour_time,tasks_time,RR_time,task_start_ends_tmp,resource_uses_tmp,RR_logs_tmp,model_dict)
            # for m in RR_time:
            #     print(RR_time[m][-1][1], end=", ")
            # print()

            # tmp={"时间（ms）": times_serial}
            # for model_name in task_start_ends:
            #     tmp[model_name]=tasks_time[model_name]

            for model_name in task_start_ends:
                count_charts[model_name].line_chart(pd.DataFrame({"时间（ms）": tasks_time[model_name][0], "排队任务数量":tasks_time[model_name][1]}),use_container_width=True, x="时间（ms）")
            count_charts["total"].line_chart(pd.DataFrame({"时间（ms）": tasks_time["total"][0], "排队任务数量":tasks_time["total"][1]}),use_container_width=True, x="时间（ms）")


            resource_chart.line_chart(pd.DataFrame({"时间（ms）": resour_time[0],"资源占用类型":resour_time[1]}),use_container_width=True, x="时间（ms）")
            # fig=DrawTotal(RR_time,RR_chart,fig,ax)
            tmp={"时间（ms）": RR_time["times"]}
            for model_name in RR_time["models"]+["total"]:
                tmp[model_name]=[v[2] for v in RR_time[model_name]]
            RR_chart.line_chart(pd.DataFrame(tmp),use_container_width=True, x="时间（ms）")

            # print("analyze-to:{:.2%}, total-tasks-count:{},resource-count:{}, RR-count:{}".format((current_time-min_time)/(max_time-min_time),len(tasks_time["total"][0]),len(resour_time[0]),len(RR_time["times"])))




def GetModelMaxCount(models):
    result={}

    for model_name in models:
        result[model_name]=1

    if not os.path.exists(os.path.join(os.getcwd(),"logs/split-log.json")):
        return result

    with open(os.path.join(os.getcwd(),"logs/split-log.json"),"r", encoding='utf-8') as fp:
        latencys=json.load(fp)
        for model_name in models:
            if model_name in latencys:
                result[model_name]=max([int(v) for v in list(latencys[model_name].keys())])

    return result


def CreateLog(models: list,log_form):
    logs=""
    for model_name in models:
        time.sleep(0.2)
        logs+="start to run {} test.\n".format(model_name)
        log_form.markdown('''
            <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
                <pre>
                    <code class="shell">
                    {}
                    </code>
                </pre>
            </div>
            '''.format("".join(logs)), unsafe_allow_html=True)
        
        time.sleep(random.uniform(0.8,2.0))
        logs+="run {} test to end.\n".format(model_name)
        log_form.markdown('''
            <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
                <pre>
                    <code class="shell">
                    {}
                    </code>
                </pre>
            </div>
            <br>
            '''.format("".join(logs)), unsafe_allow_html=True)
        
    logs+="run reply gather.\n"
    log_form.markdown('''
        <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
            <pre>
                <code class="shell">
                {}
                </code>
            </pre>
        </div>
        <br>
        '''.format("".join(logs)), unsafe_allow_html=True)
    
    time.sleep(0.05)
    logs+="start ok."
    log_form.markdown('''
        <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
            <pre>
                <code class="shell">
                {}
                </code>
            </pre>
        </div>
        <br>
        '''.format("".join(logs)), unsafe_allow_html=True)

def PullLogs():
    pass

def UpdateLogs(log_form):
    

    with open(os.path.join(os.getcwd(),"logs/server_log.txt"),"r", encoding='utf-8') as fp:
        logs=fp.readlines()

    log_form.markdown('''
    <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
        <pre>
            <code class="shell">
            {}
            </code>
        </pre>
    </div>
    <br>
    '''.format("".join(logs)), unsafe_allow_html=True)

    st.success("日志更新至: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def ControlSystem():
    st.markdown("#### 状态查询：")
    usersDatabase=database.ReadUsersDatabase()

    PullLogs()
    logs="find no logs."
    if not os.path.exists(os.path.join(os.getcwd(),"logs/server_log.txt")):
        # run
        pass
    else:
        with open(os.path.join(os.getcwd(),"logs/server_log.txt"),"r", encoding='utf-8') as fp:
            logs=fp.readlines()

    # log_form=st.code("".join(logs),language="shell")
    log_form=st.markdown('''
    <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
        <pre>
            <code class="shell">
            {}
            </code>
        </pre>
    </div>
    <br>
    '''.format("".join(logs)), unsafe_allow_html=True)

    if st.button("更新日志"):
        UpdateLogs(log_form)

    expander = st.expander("系统开关")
    expander.markdown("###### 子模型数量:")
    deployment={}

    childs_count_info=GetModelMaxCount(list(usersDatabase["models"].keys()))
    for model_name in usersDatabase["models"]:
        value=expander.slider("{}".format(model_name),min_value=0,max_value=childs_count_info[model_name],value=1 if model_name not in st.session_state else min(st.session_state[model_name],childs_count_info[model_name]),step=1)
        deployment[model_name]=value

    for k,v in deployment.items():
        if v<1:
            del deployment[k]

    if expander.button("部署"):
        # restart system
        log_form.markdown('''
        <div style="border: 1px solid black; border-radius: 3px; padding: 2px,border="1"">
            <pre>
                <code class="shell">
                restarting the system...\nplease wait ...
                </code>
            </pre>
        </div>
        <br>
        ''', unsafe_allow_html=True)

        time.sleep(1)
        CreateLog(list(deployment.keys()),log_form)

def ViewLogs():
    pass

def GetIp()->str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("114.114.114.114", 80))
        return s.getsockname()[0]
    except Exception as ex:
        return "127.0.0.1"

def ShowInterface():
    st.markdown('''
    #### 远程调用接口：

    ###### 服务器信息：
    ```shell
    服务器IP: {}
    服务器Port: {}
    ```
    '''.format(GetIp(),8500))

    st.markdown('''
    ###### 调用接口信息：
    > `RequestInfo.data` and `ReplyInfo.result`是输入/输出数据字典格式的字符串表示，例如`"{data: [[1.3, 4.5], [1, 2.0]]}"`

    ```shell
    syntax = "proto3";

    message RequestInference {
        string modelname = 1                // 将使用的推理服务，例如 "vgg19"
        string data = 2;                    // 待推理的数据, 例如 "{data: [[1.3, 4.5], [1, 2.0]]}"
    }

    message ReplyInference {
        int32 status =1;                    // 计算状态，1：成功；0：失败
        string result = 2;                  // 推理结果, 例如 "{output: [0.8]}"
        string info =3;                     // 存在warning或者error时，记录在此字段中，通常为空
    }

    message RequestInfo {}

    message ReplyInfo {
        string ip = 1;                      // 调用IP
        int32 port=2;                       // 调用端口
        repeated string modelnames=3;       // 支持的模型，字符串数组，例如：{"vgg19","resnet50"}
    }

    service DLIRService {
        rpc DoInference (RequestInference) returns (ReplyInference);    // 请求推理
        rpc GetService (RequestInfo) returns (ReplyInfo);               // 查询部署的模型
    }
    ```
    ''')

    st.markdown('''
    ###### 相关介绍:
    本系统的服务调用基于`gRPC`协议，官网：https://grpc.io
    > 它可以通过对负载平衡、跟踪、健康检查和身份验证的可插拔支持，有效地连接数据中心内和跨数据中心的服务。它还适用于将设备、移动应用程序和浏览器连接到后端服务。

    `gRPC`是一个高性能、开源的通用RPC框架，支持多种语言和平台：
    * C# / .NET
    * C++
    * Dart
    * Go
    * Java
    * Kotlin
    * Node
    * Objective-C
    * PHP
    * Python
    * Ruby

    以下是中使用gRPC进行通信的一般基本步骤:
    1. 定义`protobuf`文件：gRPC使用protobuf作为数据交换的格式。在`protobuf`文件中定义服务和消息类型，然后使用`protobuf`编译器生成`指定语言`的代码。

    2. 实现服务端：实现服务器程序，使用生成的`指定语言`代码和`gRPC`库创建一个`gRPC`服务器，并注册服务处理程序，以便处理客户端请求。

    3. 实现客户端：实现客户端程序，使用生成的`指定语言`代码和`gRPC`库创建一个`gRPC`通道，然后创建客户端存根，调用服务器提供的服务。
    '''.format(GetIp(),8500))
