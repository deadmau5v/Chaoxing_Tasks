"""
生产者
"""
import time
from threading import Thread

import redis
import consumer

db = redis.Redis()
db.keys()

while True:
    now = time.localtime()
    if now.tm_min > 30:
        m = 60 - now.tm_min
    else:
        m = 30 - now.tm_min
    # 算出下一个整点 和 下一个半点

    time.sleep(m * 60 - (60 - now.tm_sec))
    now = time.localtime()
    times = db.keys("*:time")
    for i in times:
        _i = i.decode().split(":")
        user = _i[0]
        if db.get(user + ":send") == b"true":
            continue
        password = db.get(user + ":password").decode()
        mail = db.get(user + ":email").decode()

        i = db.get(i)
        i = i.decode().split("|")
        i[0] = int(i[0])
        i[1] = int(i[1])
        if i[2] == 'pm':
            i[0] = i[0] + 12
        if i[0] == now.tm_hour and i[1] == now.tm_min:
            print("send")
            t = Thread(target=consumer.send_mail, args=(user, password, mail))
            t.start()
            db.set(user + ":send", "true")
            db.expire(user + ":send", 60 * 60 * 12)
            print("send ok" + user)
