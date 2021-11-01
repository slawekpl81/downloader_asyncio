import asyncio
from target_cls import Target
from config import path as source
from redis_con import redis

if __name__ == '__main__':
    print(f'connect with redis: {"OK" if redis.ping() else "ERROR"}')

    download_file = Target(source)
    asyncio.run(download_file.get_head())
    asyncio.run(download_file.download())

    print('flush')
    redis.flushdb()
