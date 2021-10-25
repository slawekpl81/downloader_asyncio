import aiohttp
import asyncio
import os
import time
from shutil import copyfileobj
from tabulate import tabulate
from config import path as source

chunk_size = 2 ** 20

DOWNLOADED_DATA = dict()


def print_table(counter, downloaded, range):
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
    async with session.get(path, headers=head) as resp:
        with open(f'./temp/temp{counter}.tmp', 'wb') as fd:
            async for chunk in resp.content.iter_chunked(chunk_size):
                fd.write(chunk)
                print_table(counter, fd.tell(), range)


def get_filename(path):
    return path.split('/')[-1]


def make_file(filename):
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
            part = int(file_size / 12)
            prev = 0
            next = part
            counter = 1
            while next <= file_size:
                head = {'Range': f'bytes={prev}-{next}'}
                range = next - prev
                tasks.append(asyncio.create_task(
                    download(path, counter, head, range, session)))
                prev = next + 1
                next += part
                counter += 1
            else:
                next = file_size
                head = {'Range': f'bytes={prev}-{next}'}
                range = next - prev
                tasks.append(asyncio.create_task(
                    download(path, counter, head, range, session)))

            await asyncio.gather(*tasks)
    stop_time = time.time()
    return file_size, (stop_time - start_time)


if __name__ == '__main__':
    path = source
    file_size, timeit = asyncio.run(multipatrs_download(path))
    file_size = file_size // 1000000
    filename = get_filename(path)
    make_file(filename)
    print(
        f'downloaded {file_size}MB in {int(timeit)}sec. => {(file_size / timeit):.2f}MB/sec')
