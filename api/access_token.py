import redis

redis_client = redis.StrictRedis(host = 'redis', port = '127.0.0.1:6379', db = 0, decode_responses=True)

def set_access_token(user_id: str, token: str):
    redis_client.set(token, user_id, ex=3600)

def get_user_id(token):
    return redis_client.get(token)

def delete_access_token(token):
    redis_client.delete(token)