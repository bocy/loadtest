#!/usr/bin/env python
# coding: utf-8

"""
# @File      : monitor.py
# @Copyright : bocy
# @Author    : bocy
# @Time      : 2019/5/27 11:32
# @Desc      :
"""

import docker
import json
import time
import threading
from ssh2.session import Session
import socket

docker_servers = ["172.29.165.49", "172.29.165.155", "172.29.165.60"]

result = {}


class DockerThread(threading.Thread):
    def __init__(self, container, count):
        threading.Thread.__init__(self)
        self.name = container.name.split(".")[0].replace("-", "_")
        self.container = container
        self.count_number = count

    def run(self):
        # data = {}
        t1 = time.time()
        print("start {} at {}\n".format(self.name, time.strftime("%H:%M:%S")))
        stats_data = get_docker_cpu(container=self.container, count=self.count_number)
        result[self.name] = stats_data


class LinuxThread(threading.Thread):
    def __init__(self, info, count):
        threading.Thread.__init__(self)
        self.name = info.get("name")
        self.info = info
        self.count = count

    def run(self):
        # data = {}
        print("start {} at {}\n".format(self.name, time.strftime("%H:%M:%S")))
        stats_data = get_linux_cpu(self.info, self.count)
        result[self.name] = stats_data


def get_containers(docker_servers):
    containers = []
    for server in docker_servers:
        client = docker.DockerClient(base_url="tcp://{}:2375".format(server))
        containers.extend(client.containers.list())
    return containers


def get_docker_cpu(container, count):
    stats_it = container.stats()
    data = []
    for i in range(count):
        try:
            stats_data = json.loads(stats_it.__next__().decode())
            if stats_data.get("precpu_stats").get("system_cpu_usage") is None:
                stats_data = json.loads(stats_it.__next__().decode())
            pre_total_usage = stats_data.get("precpu_stats").get("cpu_usage").get("total_usage")
            pre_system_usage = stats_data.get("precpu_stats").get("system_cpu_usage")
            total_usage = stats_data.get("cpu_stats").get("cpu_usage").get("total_usage")
            system_usage = stats_data.get("cpu_stats").get("system_cpu_usage")
            cpu_nums = stats_data.get("cpu_stats").get("online_cpus")
            if system_usage is None or pre_system_usage is None:
                continue
            total_delta = total_usage - pre_total_usage
            system_delta = system_usage - pre_system_usage
            if total_delta > 0.0 and system_delta > 0.0:
                cpu_percent = total_delta/system_delta * cpu_nums * 100.0
            else:
                cpu_percent = 0.00
            data.append(cpu_percent)
        except Exception:
            data.append(0.00)

    # print("docker cpu data:{}".format(data))
    return "{:.2f}".format(sum(data)/len(data))


def get_linux_cpu(connect_info, count):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((connect_info.get("host"), connect_info.get("port")))
    s = Session()
    s.handshake(sock)
    # s.userauth_password(connect_info.get("user"), connect_info.get("pwd"))
    if "key" in connect_info:
        s.userauth_publickey_fromfile(connect_info.get("user"), connect_info.get("key"), passphrase="")
    elif "pwd" in connect_info:
        s.userauth_password(connect_info.get("user"), connect_info.get("pwd"))
    cpu_data = []
    for i in range(count):
        chan = s.open_session()
        chan.execute("sar 1 1 | grep Average | awk '{print(100-$8)}'")
        size, data = chan.read()
        if size > 0:
            cpu_data.append(float(data.decode().strip()))
        # time.sleep(1)
    # print("linux cpu data: {}".format(cpu_data))
    return "{:.2f}".format(sum(cpu_data)/len(cpu_data))


def monitor_server(count, linux_servers, docker_servers):
    time.sleep(20)
    t1 = time.time()
    # servers = [{
    #     "name": "MongoDB",
    #     "host": "172.29.205.232",
    #     "port": 22,
    #     "user": "ec2-user",
    #     "pwd": "123456"
    # }]
    threads = []
    containers = get_containers(docker_servers)
    for container in containers:
        # print("start thread %s" % container.name)
        thread = DockerThread(container, count=count)
        thread.start()
        threads.append(thread)
    for server in linux_servers:
        thread = LinuxThread(server, count)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print("总共耗时：{}".format(time.time()-t1))
    print(result)
    return result


if __name__ == '__main__':
    # main()
    pass
    # servers = [{
    #     "name": "MongoDB",
    #     "host": "172.29.205.232",
    #     "port": 22,
    #     "user": "ec2-user",
    #     "pwd": "123456"
    # }]
    # for s in servers:
    #     print(get_linux_cpu(s, 3))
