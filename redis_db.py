import redis


class RedisDB:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def flushall(self):
        self.redis.flushall()

    def save(self):
        self.redis.save()

    def add_session(self, session):
        self.redis.set(session + ':session', 'true')
        self.redis.expire(session + ':session', 86400)  # 设置过期时间为一天

    def get_session(self, session) -> bool:
        return True if self.redis.get(session + ':session') == b'true' else False


if __name__ == '__main__':
    pass
