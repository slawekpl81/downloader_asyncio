import aiohttp
import asyncio
import os
import time
from shutil import copyfileobj
from tabulate import tabulate

chunk_size = 2 ** 20
MB50 = 'http://ipv4.download.thinkbroadband.com/50MB.zip'
MB100 = 'http://ipv4.download.thinkbroadband.com/100MB.zip'
MB512 = 'http://ipv4.download.thinkbroadband.com/512MB.zip'
GB1 = 'http://ipv4.download.thinkbroadband.com/1GB.zip'

APP = {'1': MB50,
       '2': MB100,
       '3': MB512,
       '4': GB1,
       '5': 'https://cdn.pixabay.com/photo/2019/01/06/14/08/frankfurt-3917054_960_720.jpg'}

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
    # path = 'https://cdn.pixabay.com/photo/2019/01/06/14/08/frankfurt-3917054_960_720.jpg'
    # path = 'https://wallpapercave.com/wp/wp2646303.jpg'
    # path = 'https://www.technocrazed.com/wp-content/uploads/2015/12/beautiful-wallpaper-download-14-640x360.jpg'
    # path = 'http://ipv4.download.thinkbroadband.com/1GB.zip'
    # path = 'http://ipv4.download.thinkbroadband.com/100MB.zip'

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
    while True:
        print('asyncio downloader')
        print('please paste url file for downloading or select file for speed test downloading:')
        print('1: 50MB.zip')
        print('2: 100MB.zip')
        print('3: 512MB.zip')
        print('4: 1GB.zip')
        answer = input('/>')

        if answer in APP:
            print(APP[answer])
            path = APP[answer]
        else:
            print(answer)
            path = answer
        file_size, timeit = asyncio.run(multipatrs_download(path))
        file_size = file_size//1000000
        filename = get_filename(path)
        make_file(filename)
        print(f'downloaded {file_size}MB in {int(timeit)}sec. => {(file_size / timeit):.2f}MB/sec')
        break
