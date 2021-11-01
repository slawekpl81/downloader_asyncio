import asyncio
import time

import aiohttp
from typing import List, Tuple, Optional

from app_types import RespHead
from app_methods import set_parts, get_filename, make_file_from_redis, download_to_redis


class Target:
    """object to download"""

    def __init__(self, path):
        self.path: str = path
        self.resp_status = None
        self.multi_download = None
        self.file_size = None
        # get_head(self)
        # self.resp_status, self.multi_download, self.file_size
        self.parts_to_download: Optional[List[Tuple[int, int]]] = None  # set_parts(self.file_size)
        self.file_name: str = get_filename(self.path)
        self.timing = None

    async def get_head(self):
        """get header to check base info"""
        async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
            async with session.head(self.path) as resp:
                # if str(resp.status)[0] in ('3', '4', '5'):
                #     return
                self.file_size = int(resp.headers["Content-Length"])
                self.multi_download = resp.headers['Accept-Ranges']
                self.resp_status = resp.status
        await session.close()

    def timer(self):
        print(f'downloaded {self.file_size/ 1000000}MB in {int(self.timing)}sec.'
              f' => {self.file_size/ 1000000 / self.timing:.2f}MB/sec')

    async def download(self):
        self.parts_to_download = set_parts(self.file_size)
        start_time = time.time()
        async with aiohttp.ClientSession(cookie_jar=aiohttp.DummyCookieJar()) as session:
            tasks = []
            for counter, part in enumerate(self.parts_to_download):
                head = {'Range': f'bytes={part[0]}-{part[1]}'}
                tasks.append(asyncio.create_task(
                    download_to_redis(self.path, counter, head, session)))
            await asyncio.gather(*tasks)
        stop_time = time.time()
        self.timing = stop_time - start_time
        make_file_from_redis(self.file_name, len(self.parts_to_download))
        self.timer()
        print('download')


if __name__ == '__main__':
    pass
