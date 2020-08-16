#!/usr/bin/env python
# coding: utf-8

"""
# @File      : run.py
# @Copyright : Transsnet.Inc
# @Author    : Ruijun.Peng
# @Time      : 2019/5/28 17:55
# @Desc      :
"""

from subprocess import Popen, PIPE
import os
from monitor import monitor_server
import time
import json
import re
from jinja2 import Environment, FileSystemLoader

# cmd = 'C:\\soft\\apache-jmeter-5.1.1\\bin\\jmeter.bat'
cmd = 'C:\\apache-jmeter-4.0\\bin\\jmeter.bat'
script_path = 'C:\\script\\single'
os.chdir("C:\\apache-jmeter-4.0\\bin\\")
files = [f for f in os.listdir(script_path) if f.endswith(".jmx")]
fda = open("data.txt", "w", encoding="utf-8")
# ssh_key_file_path = "C:\\TEMP\\uat-Ireland-ops.pem"
# servers = [{
#         "name": "MongoDB",
#         "host": "172.29.164.137",
#         "port": 22,
#         "user": "ec2-user",
#         "key": "C:\\TEMP\\uat-Ireland-ops.pem"
#     }]
servers = [{
        "name": "MongoDB",
        "host": "172.29.164.137",
        "port": 22,
        "user": "ec2-user",
        "key": "C:\\TEMP\\uat-Ireland-ops.pem"
    }
    ]
docker_servers = [
    "172.29.165.208", "172.29.165.60",
    "172.29.165.49","172.29.165.155",
    # "172.29.165.90", "172.29.165.109"
]
report_time = time.strftime("%Y%m%d_%H%M")
report_path = "report/{}".format(report_time)
if os.path.exists(report_path):
    os.rmdir(report_path)
else:
    os.mkdir(report_path)
all_data = []
for f in files:
    result = {}
    jmeter_result = ""
    script = os.path.join(script_path, f)
    with open(script, encoding="utf-8") as fd:
        data = fd.read()
        result["uri"] = re.findall('HTTPSampler.path">(.*?)</stringProp>', data)[-1]
    script_name = f.split(".")[0]
    result["name"] = script_name
    result["strat_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    # commond = "{} -n -t {}".format(cmd, script)
    commond = "{} -n -t {} -l jtl/{}.jtl -e -f -o {}/{}".format(cmd, script, script_name, report_path, script_name)
    proc = Popen(commond)
    result["monitor_result"] = monitor_server(250, servers, docker_servers).copy()
    return_code = proc.wait()
    with open("jmeter.log") as f:
        jmeter_result = f.read()
    # thread_number = re.findall("StandardJMeterEngine: Starting (.*?) threads", jmeter_result)[0]
    # result["thread_num"] = thread_number
    result['sampleCount'] = re.findall("summary =(.*?) in", jmeter_result)[-1].strip()
    result["tps"] = re.findall("=(.*?)/s Avg", jmeter_result)[-1].split("=")[1].strip()
    result['meanResTime'] = re.findall("Avg:(.*?) Min", jmeter_result)[-1].strip()
    result['errorRet'] = re.findall("\\((.*?)%\\)", jmeter_result)[-1].strip()
    print(result)
    fda.write(str(result) + "\n")
    all_data.append(result)
        # time.sleep(5)

    # with open("../report/%s" % script_name) as fd:
    #     data = json.loads(fd.read()).get("Total")
    #     result["sampleCount"] = data.get("sampleCount")
    #     result["tps"] = data.get("throughput")
    #     result["meanResTime"] = data.get("meanResTime")
    #     result["90ResTime"] = data.get("pct1ResTime")
    #     result["successRet"] = data.get("errorPct")

    # return_code = proc.wait()
    # with open('jmeter.log', encoding='utf-8') as fd:
    #     jmeter_result = fd.read()

env = Environment(loader=FileSystemLoader('C:\\Users\\perfadmin\\Documents\\loadtest'))
template = env.get_template('base.html')
with open("Report{}.html".format(time.strftime("%Y-%m-%d_%H%M")), "w", encoding="utf-8") as f:
    content = template.render(all_data=all_data)
    f.write(content)
fda.close()
