from fastapi import HTTPException
import jwt
import string
import random
# for python 3.12
# import redis
# for python 3.10
import aioredis

redis_client = None
SECRET_KEY = 'secret_key'

async def init_redis():
    global redis_client
    # for python 3.12
    # redis_client = redis.StrictRedis(host = '127.0.0.1', port = '25100', db = 0, decode_responses=True)
    # for python 3.10
    redis_client = await aioredis.from_url('redis://127.0.0.1:25100', db = 0, decode_responses=True)

async def close_redis():
    if redis_client:
        redis_client.close()
        await redis_client.wait_closed()

async def set_access_token(user_id: int):
    if redis_client:
        rand = "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k = 16))
        token = jwt.encode({"user_id": user_id, 'rand': rand}, SECRET_KEY, algorithm = "HS256")
        await redis_client.set(user_id, token)
        return token

async def chk_access(token):
    if redis_client:
        payload = jwt.decode(token, 'secret_key', algorithms=["HS256"])
        if await redis_client.get(payload['user_id']) == token: 
            return payload['user_id']
        raise HTTPException(status_code=400, detail="Invalid Access")

async def delete_access_token(token):
    if redis_client:
        payload = jwt.decode(token, 'secret_key', algorithms=["HS256"])
        if await redis_client.get(payload['user_id']) == token:
            await redis_client.delete(payload['user_id'])
            return payload['user_id']
        raise HTTPException(status_code=400, detail="Invalid Access")