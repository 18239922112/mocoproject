# -*- coding: utf-8 -*-
"""
@Time ： 2024/2/2 14:39
@Auth ： 七月
@File ：mocoRequest.py
@IDE ：PyCharm
"""
import json

from flask import Flask, request, jsonify, render_template
from conncetMysql import connect_mysql, mysqlResult, mysqlAllResult
from makeLog import Logger
import socket


app = Flask(__name__,static_url_path='/static')

log = Logger()


def get_local_ip():
    '''
    获取本机ip
    :return:
    '''
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

@app.before_request
def get_call_ip():
    '''
    获取调用者的ip
    :return:
    '''
    # 尝试获取 X-Forwarded-For 头部中的 IP 地址
    if 'X-Forwarded-For' in request.headers:
        # 使用nginx部署的时候需要通过这种方式获取真实的客户端ip，不然的话返回的就是代理服务器的地址就不正确了
        client_ip = request.headers['X-Forwarded-For'].split(',')[0].strip()  # 取第一个 IP 并去除空格
    else:
        client_ip = request.remote_addr
    log.info('请求来自于' + client_ip)


@app.route('/moco')
def index():
    return render_template('index.html')





@app.route('/moco/addMoco',methods=['POST'])
def addMoco():
    data = request.json
    #print(data)
    apiname = data["apiname"]
    apipath = data["apipath"]
    apitext = data["apitext"]
    isChecked = data["isChecked"]
    sql = "select  apitext from apitest where apipath=%s;"
    query_result = connect_mysql(sql, params=apipath)

    if query_result:
        log.info('%s:该接口路径已使用，请核对后再添加'%apipath)
        return jsonify({"code":300,"msg":"该接口路径已使用，请核对后再添加"})
    else:
        sql = "insert into apitest (apiname,apipath,apitext,isEnable) VALUES(%s,%s,%s,%s);"
        params = (apiname,apipath,apitext,isChecked)
        connect_mysql(sql,params)
        log.info('添加接口成功,路径为：%s'%apipath)
        return jsonify({"code":200,"msg":"添加接口成功"})

@app.route('/moco/delMoco',methods=['POST'])
def delMoco():
    data = request.json
    apipath = data["apipath"]

    sql = "delete from apitest where apipath=%s;"

    try:
        connect_mysql(sql, params=apipath)
        return jsonify({"code": 200, "msg": "删除成功"})
    except Exception as e:
        log.error(e)
        return jsonify({"code":"500","msg":"sql执行报错了错误原因:%s"%e})




@app.route('/moco/editMoco',methods=['POST'])
def editMoco():
    data = request.json
    # print(data)
    apiname = data["apiname"]
    apipath = data["apipath"]
    apitext = data["apitext"]
    isEnable = data["isChecked"]
    sql = "update apitest set  apiname=%s,apitext=%s,isEnable=%s where apipath=%s;"
    params = (apiname,apitext,isEnable,apipath)
    try:
        connect_mysql(sql, params=params)
        return jsonify({"code": 200, "msg": "修改成功"})
    except Exception as e:
        log.error(e)
        return jsonify({"code":"500","msg":f"sql执行报错了错误原因:{e}"})






@app.route('/<path:apipath>',methods=['GET','POST'])
def mocoServer(apipath):

    sql = "select  apitext,isEnable from apitest where apipath=%s;"
    query_result = connect_mysql(sql,params='/'+apipath)
    if query_result:
        apitext,isEnable = mysqlResult(query_result)
        if isEnable == 0:
            try:
                return json.loads(apitext)
            except Exception as e:
                log.error(e)
                return jsonify({"code":"500","msg":f"请检查你的接口数据格式是否正确"})
        else:
            log.info('%s此接口已停用'%apipath)
            return jsonify({"code":"500","msg":"此接口已停用"})
    else:
        log.info('%s此接口不存在请核对后再请求' % apipath)
        return jsonify({"code":"500","msg":"此接口不存在请核对后再请求"})

@app.route('/moco/queryAll',methods=['GET'])
def queryAll():
    #sql = "select  * from apitest order by id desc;"
    sql = "select  * from apitest order by id desc limit 0,10;"
    query_result = connect_mysql(sql)
    query_all = mysqlAllResult(query_result)
    return jsonify(query_all)


@app.route('/moco/queryLike',methods=['POST'])
def queryLike():
    data = request.json

    apipath = data["apipath"]

    sql = "select  * from apitest  where apipath like %s order by id desc limit 0,10;"

    query_result = connect_mysql(sql,params=('%' + apipath + '%'))

    query_all = mysqlAllResult(query_result)
    return jsonify(query_all)



@app.route('/moco/queryApi',methods=['POST'])
def queryApi():
    data = request.json

    apipath = data["apipath"]

    sql = "select  apitext,isEnable from apitest where apipath=%s;"
    query_result = connect_mysql(sql, params=apipath)
    apitext,isable = mysqlResult(query_result)

    return jsonify({"apitext":apitext,"isable":isable})



@app.route('/moco/queryLimit',methods=['POST'])
def queryLimit():
    data = request.json
    page = data["page"]

    sql = "select  * from apitest order by id desc limit %s,10;"

    query_result = connect_mysql(sql,params=page)
    query_all = mysqlAllResult(query_result)
    return jsonify(query_all)





@app.route('/moco/queryCount', methods=['GET'])
def queryCount():


    sql = "select  count(*) from apitest;"

    count = connect_mysql(sql)
    return jsonify({"count":count})

