# loadtest
基于jmeter的自动化性能测试


## 主要是做单接口查询性能的自动化测试与监控

该项目基于之前shell+jmeter自动化性能测试的python改进版本
https://testerhome.com/topics/4264

但是有不一样的地方：
1. 此项目基于python脚本
2. 此项目每个用例会生成jmeter自带的报告
3. 此项目能支持docker服务的CPU监控


## 运行环境：
```
python3.6
pip install jinja2==2.10
pip install docker==3.7.1
```

## 初始化

修改run.py中关于程序和脚本的目录，应用和数据库服务器已经docker服务器目录，即可执行run.py
```
#jmeter程序目录：
cmd = 'C:\\apache-jmeter-4.0\\bin\\jmeter.bat'
#脚本存储目录
script_path = 'C:\\script\\single'
# linux服务器列表，注意如果用key的方式连接ssh，指定对的秘钥路径
servers = [{
        "name": "MongoDB",
        "host": "172.29.164.137",
        "port": 22,
        "user": "ec2-user",
        "key": "C:\\TEMP\\uat-Ireland-ops.pem"
    },
    # 用户名密码形式的ssh连接{
    #     "name": "MongoDB",
    #     "host": "172.29.205.232",
    #     "port": 22,
    #     "user": "ec2-user",
    #     "pwd": "123456"
    # }
    ]
# docker服务器器列表
docker_servers = [
    "172.29.165.208", "172.29.165.60",
    "172.29.165.49","172.29.165.155",
    # "172.29.165.90", "172.29.165.109"
]
```
