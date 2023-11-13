import random

import flask
import requests
from flask import Flask, render_template
from urllib import parse

import redis_db
from api import login
from api.log import info, error
import encod
import consumer

app = Flask(__name__)
db = redis_db.RedisDB()


def random_session():
    word = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4',
            '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D',
            'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
            'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
            'Y', 'Z']
    session = ''
    for _ in range(16):
        session += random.choice(word)
    return session


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/init_cookie')
def init_cookie():
    response = flask.Response()
    session = random_session()
    response.set_cookie('SESSIONID', session)
    request = flask.request
    if request.cookies.get('SESSIONID') is None:
        db.add_session(session)
        response.content_type = 'application/json'
        data = {'status': False, 'message': '已经有cookie了'}
        response.data = flask.json.dumps(data)
        return response
    else:
        session = request.cookies.get('SESSIONID')
        if db.get_session(session):
            return {'status': False, 'message': '已经有cookie了'}
        else:
            db.add_session(session)
            return {'status': False, 'message': '已经有cookie了'}


@app.route('/api/test_login', methods=['POST'])
def test_login():
    request = flask.request
    session = request.cookies.get('SESSIONID')
    if session is None:
        error("某人 测试登录失败 原因:没有cookie")
        return {'status': False, 'message': '无权访问'}
    if not db.get_session(session):
        error("某人 测试登录失败 原因:没有cookie")
        return {'status': False, 'message': '无权访问'}
    if "python" in request.headers.get("User-Agent").lower():
        error("某人 测试登录失败 原因:UA为Python")
        return {'status': False, 'message': '无权访问'}
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None or username == '' or password == '':
        error("某人 测试登录失败 原因:用户名或密码为空 Username:" + str(username) + " Password: " + str(password))
        return {'status': False, 'message': '用户名或密码为空'}
    session = requests.Session()
    try:
        login.login(session, username, password)

    except SystemExit:
        error(str(username) + " 测试登录失败")
        return {'status': False, 'message': "登录失败"}
    info(str(username) + " 测试登录成功")
    return {'status': True, 'message': '登录成功'}


@app.route('/api/submit', methods=['POST'])
def submit():
    request = flask.request
    session = request.cookies.get('SESSIONID')
    if session is None:
        error("某人 测试登录失败 原因:没有cookie")
        return {'status': False, 'message': '无权访问'}
    if not db.get_session(session):
        error("某人 测试登录失败 原因:没有cookie")
        return {'status': False, 'message': '无权访问'}
    if "python" in request.headers.get("User-Agent").lower():
        error("某人 测试登录失败 原因:UA为Python")
        return {'status': False, 'message': '无权访问'}

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hour = data.get('hour')
    minute = data.get('minute')
    time_step = data.get('time_step')
    email = data.get('email')
    info(username + "提交了一次任务")
    if username is None or password is None or username == '' or password == '':
        error(str(username) + "失败了一次任务 原因:用户名或密码为空")
        return {'status': False, 'message': '用户名或密码为空'}

    if db.redis.get(username + ':status') == b'true':
        error(username + "失败了一次任务 原因:已经提交过了")
        return {'status': False, 'message': '已经提交过了'}

    db.redis.set(username + ':status', 'true')
    db.redis.sadd('jobs', username + "|" + password)
    db.redis.set(username + ':password', password)
    db.redis.set(username + ':time', hour + "|" + minute + "|" + time_step)
    db.redis.set(username + ':email', email)
    db.save()
    info(username + "成功提交")
    consumer.send_mail(username, password, email, "学习通作业通知 第一次订阅测试")
    return {'status': True, 'message': 'success'}


@app.route('/api/remove_mail', methods=['GET'])
def remove_mail():
    request = flask.request
    token = request.args.get('token')
    if not token:
        error("某人 取消订阅失败 原因:没有token")
        return {'status': False, 'message': '无权访问'}
    try:
        token = parse.unquote(token)  # url 解码
        data = encod.decode(token)
        data = data.split("|")
        username = data[0]
        password = data[1]
        if not password.encode() == db.redis.get(username + ":password"):
            error("某人 取消订阅失败 原因:密码错误")
            return {'status': False, 'message': '无权访问'}
        db.redis.delete(username + ":password")
        db.redis.delete(username + ":time")
        db.redis.delete(username + ":email")
        db.redis.delete(username + ":status")
        db.redis.srem('jobs', username + "|" + password)
        db.save()
        info(username + "取消订阅成功")
        return render_template('remove_mail_success.html')
    except Exception as e:
        error(str(e))
        error("某人 取消订阅失败 原因:token错误")
        return {'status': False, 'message': '无权访问'}


@app.route('/success', methods=['GET'])
def success():
    request = flask.request
    session = request.cookies.get('SESSIONID')
    if session is None:
        return {'status': False, 'message': '无权访问'}
    if not db.get_session(session):
        return {'status': False, 'message': '无权访问'}
    if "python" in request.headers.get("User-Agent").lower():
        return {'status': False, 'message': '无权访问'}
    consumer.mail_title = "学习通作业通知 第一次订阅测试"
    return render_template('success.html')


if __name__ == '__main__':
    app.run(port=5010)
