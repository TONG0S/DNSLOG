#!/usr/bin/env python
import pymysql
import os,json


config1 = os.path.join( "dnslog_", 'config.json')
global config
with open(config1, 'rb') as f:
    config = dict(json.load(f))
database_ = config["database"]
user = database_["user"]  # 用户名
password = database_["password"]  # 密码
host = database_["host"]  # 连接名称
port = database_["port"]  # port需要是int类型
db = database_["db"]  # 数据库
print(config)
conn = pymysql.connect(host=host, port=port, user=user, password=password)
cursor = conn.cursor()  # 生成游标对象
sql="create database {}".format(db)

cursor.execute(sql)  # 执行SQL语句

conn.commit()
cursor.close()
conn.close()
conn = pymysql.connect(host=host, port=port, user=user, password=password,db=db)
cursor = conn.cursor()  # 生成游标对象
sql='''create table dnsquery( user char(255),src char(255) ,domain text,dst char(255),createtime char(255))'''
cursor.execute(sql)  # 执行SQL语句

conn.commit()
sql='''create table user( user char(255),passwd char(255))'''
cursor.execute(sql)  # 执行SQL语句

conn.commit()
# 关闭连接，游标和连接都要关闭
cursor.close()
conn.close()

