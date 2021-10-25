import aiohttp
import asyncio
import os
import time
from shutil import copyfileobj
from tabulate import tabulate
from config import path as source
from redis_con import redis

chunk_size = 2 ** 20
DOWNLOADED_DATA = dict()
PARTS = 12


def print_table(counter, downloaded, range):
    """print download progress"""
    change = int(downloaded / range * 100)
    try:
        if (change - DOWNLOADED_DATA[counter]) > 5 or change == 100:
            DOWNLOADED_DATA[counter] = change
            os.system('cls' if os.name == 'nt' else 'clear')
            table = [[f'PART-{key}', f':{value}%'] for key, value in
                     DOWNLOADED_DATA.items()]
            print(tabulate(table))
    except KeyError:
        DOWNLOADED_DATA[counter] = change
        os.system('cls' if os.name == 'nt' else 'clear')
        table = [[f'PART-{key}', f':{value}%'] for key, value in
                 DOWNLOADED_DATA.items()]
        print(tabulate(table))


async def download(path, counter, head, range, session):
    """save data to temp file"""
    async with session.get(path, headers=head) as resp:
        with open(f'./temp/temp{counter}.tmp', 'wb') as fd:
            async for chunk in resp.content.iter_chunked(chunk_size):
                fd.write(chunk)
                print_table(counter, fd.tell(), range)


async def download_to_redis(path, counter, head, range, session):
    """save data to redis"""
    key = f'temp{counter}'
    async with session.get(path, headers=head) as resp:
        async for chunk in resp.content.iter_chunked(chunk_size):
            redis.rpush(key, chunk)
    #         fd.write(chunk)


def get_filename(path):
    """get filename from url"""
    return path.split('/')[-1]


def make_file(filename):
    """get temp files and create output file """
    current_dir = os.getcwd()
    all_files = os.listdir('./temp')
    all_files = sorted(all_files)
    all_files = sorted(all_files, key=len)
    files = []
    for file in all_files:
        files.append(f'{current_dir}/temp/{file}')
    with open(f'./downloads/{filename}', 'wb') as fd:
        for file in files:
            with open(file, 'rb') as f:
                copyfileobj(f, fd)
            os.remove(file)


def make_file_from_redis(filename):
    """get data in redis and create output file """
    with open(f'./downloads/{filename}', 'wb') as fd:
        for item in range(PARTS):
            key = f'temp{item}'
            data = redis.lrange(key, 0, -1)
            for piece in data:
                fd.write(piece)


async def multipatrs_download(path):
    async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
        async with session.head(path) as resp:
            print(f'Respons status:{resp.status}')
            file_size = int(resp.headers["Content-Length"])
            print(f'File size:{file_size}')
            multiparts_download = resp.headers['Accept-Ranges']
            print(f'Multiparts download:{multiparts_download}')
            if str(resp.status)[0] in ('3', '4', '5'):
                return
        async with session.get(path) as resp:
            start_time = time.time()
            tasks = []
            part = int(file_size / PARTS)
            prev = 0
            next = part
            counter = 1
            while next <= file_size:
                head = {'Range': f'bytes={prev}-{next}'}
                range = next - prev
                tasks.append(asyncio.create_task(
                    # download(path, counter, head, range, session)))
                    download_to_redis(path, counter, head, range, session)))
                prev = next + 1
                next += part
                counter += 1
            else:
                next = file_size
                head = {'Range': f'bytes={prev}-{next}'}
                range = next - prev
                tasks.append(asyncio.create_task(
                    # download(path, counter, head, range, session)))
                    download_to_redis(path, counter, head, range, session)))

            await asyncio.gather(*tasks)
    stop_time = time.time()
    return file_size, (stop_time - start_time)


if __name__ == '__main__':
    print(f'connect with redis: {"OK" if redis.ping() else "ERROR"}')
    path = source
    file_size, timeit = asyncio.run(multipatrs_download(path))
    file_size = file_size // 1000000
    filename = get_filename(path)
    # make_file(filename)
    make_file_from_redis(filename)
    print(
        f'downloaded {file_size}MB in {int(timeit)}sec. => {(file_size / timeit):.2f}MB/sec')

    # print(f'connect with redis: {"OK" if redis.ping() else "ERROR"}')
    # list_key = 'list_a'
    # #
    # redis.rpush(list_key, 12)
    #
    # for i in range(20, 25):
    #     # print(i)
    #     redis.rpush(list_key, i)
    # print(f'list: {redis.lrange(list_key, 0, -1)}')
    redis.flushdb()
    # redis.delete(list_key)
    # print(f'list: {redis.lrange(list_key, 0, -1)}')
    #
    # while True:
    #     print(f'list: {redis.brpop(list_key)}')
