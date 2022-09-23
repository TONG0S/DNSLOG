from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import pymysql
import string
import random
import os, json
from Dnslog_web.settings import BASE_DIR
import time
from django.core import signing
import hashlib
from django.core.cache import cache
# 问题。
'''
cookie  csrf 
  处理多用户
'''

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = 'CHEN_FENG_YAO'
SALT = 'www.TONG.com'
TIME_OUT = 30 * 60  # 30min
def encrypt(obj):
    """加密"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value


def create_cookie(username):
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload
    payload = {"username": username, "iat": time.time()}
    payload = encrypt(payload)
    # 3. 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    cookie = "%s.%s.%s" % (header, payload, signature)
    # 存储到缓存中
    return cookie
def decrypt(src):
    """解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw




# 通过value获取用户名
def get_username(cookie):
    print(str(cookie))
    payload = str(cookie).split('.')[1]
    payload = decrypt(payload)
    return payload['username']


def conn(requests):
    config1 = os.path.join(BASE_DIR,"dnslog_",'config.json')
    global  config
    with open(config1, 'rb') as f:
        config = dict(json.load(f))
    database_=config["database"]
    user = database_["user"]  # 用户名
    password = database_["password"]  # 密码
    host = database_["host"]  # 连接名称
    port = database_["port"]  # port需要是int类型
    db = database_["db"]  # 数据库
    sql = requests
    conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db)
    cursor = conn.cursor()  # 生成游标对象

    try:
        cursor.execute(sql)  # 执行SQL语句
        conn.commit()
        data = cursor.fetchall()
        return list(data)

    except Exception as e:
        print(e)
    cursor.close()
    conn.close()
    return False


def main(requests):
    #
    ret = requests.get_signed_cookie("is_login", default="0", salt="ban")
    username_=get_username(ret)

    if requests.method == "POST":
        # print(dict(requests.POST))
        req = dict(requests.POST)
        if 'new_domain' in req:
            conf_path = os.path.join(BASE_DIR, 'dnslog_', 'config.json')

            with open(conf_path, 'rb') as f:
                config = dict(json.load(f))
            sql = 'delete from dnsquery where user="{}"'.format(username_)
            x = conn(sql)
            domain = config["domain"]
            ran_str = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(4, 8)))
            global new_domain
            new_domain = ran_str + '.' + str(domain).strip()

            return render(requests, "index.html", {"domain": new_domain})  # 自动去templates目录下查找，setting配置文件中
        # else:
        elif 'new_A' in req:
            new_domain = new_domain
            # new_domain = "eck2xxX1h.zweather.tk"
            sql = 'select src,domain,createtime from dnsquery where domain like "%{}"'.format(new_domain)
            data = conn(sql)

            return render(requests, "index.html", {"domain": new_domain, 'AAA': data})
        elif "about" in req:
            about_code_= os.path.join(BASE_DIR, 'other_about', '1.json')
            with open(about_code_, 'rb') as f:
                about_code = dict(json.load(f))
            return render(requests, "about.html", {"code": about_code})
            
    if username_:

        # new_domain = "eck2xxX1h.zweather.tk"
        sql = 'select src,domain,createtime from dnsquery where domain like "%{}"'.format(new_domain)
        data = conn(sql)

        return render(requests, "index.html", {"domain": new_domain, 'AAA': data})
    return render(requests, "login.html", {"error": "请先登录"})

def index(requests):

    if requests.method == "POST":
        user = requests.POST.get("username")
        passw = requests.POST.get("password")

        sql = "select user,passwd from user"  # SQL语句
        data = conn(sql)
        judge = False
        if isinstance(data, list):
            for i in list(data):
                if user == i[0] and passw == i[1]:
                    judge = True
                    username_ = i[0]
                    break
        if judge:

            rep=render(requests, "index.html")  # 自动去templates目录下查找，setting配置文件中
            value=str(create_cookie(username_))
            rep.set_signed_cookie("is_login", value, salt="ban")
            # rep.set_signed_cookie("is_login", value, salt="ban", max_age=100)
            return rep

        return render(requests, "login.html", {"error": "账户密码错误"})

    return render(requests, "login.html")  # 自动去templates目录下查找，setting配置文件中


