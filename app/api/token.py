from fastapi import HTTPException
import redis
import jwt
import string
import random
# import aioredis



redis_client = None
SECRET_KEY = 'secret_key'

async def init_redis():
    global redis_client
    redis_client = redis.StrictRedis(host = '127.0.0.1', port = '25100', db = 0, decode_responses=True)
    # redis_client = await aioredis.from_url(host = '127.0.0.1', port = '25100', db = 0, decode_responses=True)

def set_access_token(user_id: int):
    if redis_client:
        rand = "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k = 16))
        token = jwt.encode({"user_id": user_id, 'rand': rand}, SECRET_KEY, algorithm = "HS256")
        redis_client.set(user_id, token)
        return token

def chk_access(token):
    if redis_client:
        payload = jwt.decode(token, 'secret_key', algorithms=["HS256"])
        if redis_client.get(payload['user_id']) == token: 
            return payload['user_id']
        raise HTTPException(status_code=400, detail="Invalid Access")

def delete_access_token(token):
    if redis_client:
        payload = jwt.decode(token, 'secret_key', algorithms=["HS256"])
        if redis_client.get(payload['user_id']) == token:
            redis_client.delete(payload['user_id'])
            return payload['user_id']
        raise HTTPException(status_code=400, detail="Invalid Access")