import streamlit as st
import os,datetime,time,random,json
import database
import socket

def GetModelMaxCount(models):
    result={}

    for model_name in models:
        result[model_name]=1

    if not os.path.exists(os.path.join(os.getcwd(),"logs/split-log.json")):
        return result

    with open(os.path.join(os.getcwd(),"logs/split-log.json"),"r") as fp:
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
    

    with open(os.path.join(os.getcwd(),"logs/server_log.txt"),"r") as fp:
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
        with open(os.path.join(os.getcwd(),"logs/server_log.txt"),"r") as fp:
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
    > `RequestInfo.data` and `ReplyInfo.result`是矩阵的字符串表示，例如`"[[1.3, 4.5], [1, 2.0]]"`

    ```shell
    syntax = "proto3";

    message RequestInference {
        string modelname = 1                // 将使用的推理服务，例如 "vgg19"
        string data = 2;                    // 待推理的数据, 例如 "[[1.3, 4.5], [1, 2.0]]"
    }

    message ReplyInference {
        int32 status =1;                    // 计算状态，1：成功；0：失败
        string result = 2;                  // 推理结果, 例如 "[0.8]"
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
