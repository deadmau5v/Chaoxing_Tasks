import base64
import json
import os

import requests as req
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

from . import configs
from .log import info
from .log import error
from .log import debug

from redis_db import RedisDB

db = RedisDB()


def get_json_data(json_path="data/users.json") -> dict:
    try:
        with open(json_path, 'r', encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding="utf-8") as f:
            f.write('{}')
        data = '{}'
    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        return {}


def save_json_data(data: dict, json_path="data/users.json") -> None:
    with open(json_path, 'w', encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


def encrypt_aes(message: str, key: str) -> str:
    """
    AES加密密码和电话号码
    :param message: 需要加密的字符串
    :param key: AES密钥
    :return: 加密后的字符串
    """
    iv = key.encode('utf-8')
    mode = AES.MODE_CBC
    cipher = AES.new(key.encode('utf-8'), mode, iv)

    byte = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size, style='pkcs7'))
    res = base64.b64encode(byte).decode()
    return res


def login(session: req.Session, username, password) -> None:
    """
    使用Session 登录到超星
    :param session: req.Session 会话类
    :param username: 用户名（电话号码）
    :param password: 密码
    :return: None
    """
    json_data = get_json_data()
    if username in json_data.keys() and db.redis.get(username) == password:
        session.cookies.update(json_data[username])
        info(f"已使用保存的Cookie登录 {username}")

        # 检查Cookie是否有效
        url = "https://i.chaoxing.com/base/cacheUserOrg"
        res = session.get("https://i.chaoxing.com/base/cacheUserOrg", headers=configs.headers)
        try:
            res.json()
            return
        except json.decoder.JSONDecodeError:
            info("Cookie已失效, 重新登录...")

    url = "https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https://i.chaoxing.com"

    # 获取初始Cookie JSESSIONID、route
    session.get(url, headers=configs.headers)

    # 登录
    url = "https://passport2.chaoxing.com/fanyalogin"

    transferKey = "u2oh6Vu^HWe4_AES"
    encode_password = encrypt_aes(password, transferKey)
    encode_username = encrypt_aes(username, transferKey)
    data = {
        "fid": -1,
        "uname": encode_username,
        "password": encode_password,
        "refer": "https%3A%2F%2Fi.chaoxing.com",
        "t": True,
        "forbidotherlogin": 0,
        "validate": "",
        "doubleFactorLogin": 0,
        "independentId": 0,
    }
    res = session.post(url, headers=configs.headers, data=data)
    if res.status_code != 200:
        error("登录失败")
        exit(1)
    if not res.json()["status"]:
        error(res.json()["msg2"])
        exit(1)
    info(f"登录成功 {username}")
    json_data[username] = session.cookies.get_dict()
    save_json_data(json_data)
    debug(f"已保存登录Cookie {username}")
