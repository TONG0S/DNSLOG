#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import socketserver
# import SocketServer
import struct,os,json
from datetime import datetime
import socket as socketlib
import pymysql
# from DNs.settings import BASE_DIR
def conn_(src_ip,domain,dst_ip):
    database_=config["database"]
    user = database_["user"]  # 用户名
    password = database_["password"]  # 密码
    host = database_["host"]  # 连接名称
    port = database_["port"]  # port需要是int类型
    db = database_["db"]  # 数据库
    print(database_)

    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db)
        cursor = conn.cursor()  # 生成游标对象
        # sql = "show tables"  # SQL语句
        # print(requests)
        temp = domain.replace(".", "")
        z = temp.isalnum()
        if z:
            now_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            user = database_["default_name"]
            sql = 'insert into dnsquery(user,src,domain,dst,createtime) VALUE("{}","{}","{}","{}","{}")'.format(user,
                                                                                                                src_ip,
                                                                                                                domain,dst_ip,
                                                                                                                now_time)
            print(sql)
            cursor.execute(sql)  # 执行SQL语句

            conn.commit()
        else:
            print("可能存在攻击行为~")
    except Exception as e:
        print(e)
        exit()
    # data = cursor.fetchall()  # 通过fetchall方法获取所有数据

    # 关闭连接，游标和连接都要关闭
    cursor.close()
    conn.close()
    return "???*****???"

class SinDNSQuery:
    def __init__(self, data):
        i = 1
        self.name = ''
        i = 1
        name = ""
        p = data
        while True:
            d = p[i]
            if d == 0:
                break
            if 1<d < 32:
                name = name + '.'
            else:
                name = name + '.' + chr(d)
            i = i + 1
        # self.name = name.replace(".", "")
        name = name.replace("..", "#")
        name = name.replace(".", "")
        self.name = name.replace("#", ".")

        self.querybytes = p[0:i + 1]
        (self.type, self.classify) = struct.unpack('>HH', p[i + 1:i + 5])

        self.len = i + 5
    def getbytes(self):
        return self.querybytes + struct.pack('>HH', self.type, self.classify)
# DNS Answer RRS
# this class is also can be use as Authority RRS or Additional RRS
class SinDNSAnswer:
    def __init__(self, ip):
        self.name = 49164
        self.type = 1
        self.classify = 1
        self.timetolive = 190
        self.datalength = 4
        self.ip = ip
    def getbytes(self):
        res = struct.pack('>HHHLH', self.name, self.type, self.classify, self.timetolive, self.datalength)
        s = self.ip.split('.')
        res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))
        return res
# DNS frame
# must initialized by a DNS query frame
class SinDNSFrame:
    def __init__(self, data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
        # print(self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        self.query = SinDNSQuery(data[12:])  #格式吹
    def getname(self):
        return self.query.name
    def setip(self, ip):
        self.answer = SinDNSAnswer(ip)
        self.answers = 1
        self.flags = 33152
    def getbytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition)
        res = res + self.query.getbytes()
        if self.answers != 0:

            res = res + self.answer.getbytes()
        return res
# A UDPHandler to handle DNS query
class SinDNSUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        #数据处理
        dns = SinDNSFrame(data)
        socket = self.request[1]
        namemap = SinDNSServer.namemap

        #下一步
        if(dns.query.type==1):
            name = dns.getname()
            toip = None
            ifrom = "map"
            if namemap.__contains__(name):  #判断是否在键中
                toip = namemap[name]
            elif namemap.__contains__('*'):
                toip = namemap['*']
            else:

                try:

                    toip = socketlib.getaddrinfo(name,0)[0][4][0]
                    ifrom = "sev"
                except Exception as e:
                    print('get ip fail')
            if toip:
                dns.setip(toip)
            if config['domain'] in name:
                # info=[self.client_address[0],name,toip]

                print('%s: %s-->%s (%s)'%(self.client_address[0], name, toip, ifrom))
                conn_(self.client_address[0],name,toip)
                # t = threading.Thread(target=conn_, args=(self.client_address[0],name,toip))

            socket.sendto(dns.getbytes(), self.client_address)
        else:

            socket.sendto(data, self.client_address)


class SinDNSServer:
    def __init__(self, port=53):
        SinDNSServer.namemap = {}
        self.port = port
    def addname(self, name):
        SinDNSServer.namemap=name
        # print(config)
        # print(SinDNSServer.namemap)
    def start(self):
        HOST, PORT = "0.0.0.0", self.port
        server = socketserver.UDPServer((HOST, PORT), SinDNSUDPHandler)
        server.serve_forever()
# Now, test it
def run():
    sev = SinDNSServer()
    config1 = os.path.join('config.json')

    global  config
    with open(config1, 'rb') as f:
        config = dict(json.load(f))
    print(config)

    info=config["info"]

    sev.addname(info)

    sev.start() # start DNS server
run()

