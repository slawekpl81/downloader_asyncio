from redis_con import redis
from typing import List, Tuple

chunk_size = 2 ** 20


def set_parts(size):
    """set size of parts to download data"""
    parts = 10
    part = size // parts
    parts_to_download = [[i * part, (i + 1) * part] for i in range(parts)]
    parts_to_download = [[x + 1, y] if x != 0 else [x, y] for [x, y] in parts_to_download]
    parts_to_download[-1][1] = size
    print(parts_to_download)
    return parts_to_download


# def print_table(counter, downloaded, range):
#     """print download progress"""
#     change = int(downloaded / range * 100)
#     try:
#         if (change - DOWNLOADED_DATA[counter]) > 5 or change == 100:
#             DOWNLOADED_DATA[counter] = change
#             os.system('cls' if os.name == 'nt' else 'clear')
#             table = [[f'PART-{key}', f':{value}%'] for key, value in
#                      DOWNLOADED_DATA.items()]
#             print(tabulate(table))
#     except KeyError:
#         DOWNLOADED_DATA[counter] = change
#         os.system('cls' if os.name == 'nt' else 'clear')
#         table = [[f'PART-{key}', f':{value}%'] for key, value in
#                  DOWNLOADED_DATA.items()]
#         print(tabulate(table))


async def download_to_redis(path, counter, head, session):
    """save part data to redis"""
    key = f'temp{counter}'
    async with session.get(path, headers=head) as resp:
        async for chunk in resp.content.iter_chunked(chunk_size):
            redis.rpush(key, chunk)


def get_filename(path: str) -> str:
    """get filename from url"""
    return path.split('/')[-1]


def make_file_from_redis(filename, parts):
    """get data from redis and create output file """
    with open(f'./downloads/{filename}', 'wb') as fd:
        for item in range(parts):
            key = f'temp{item}'
            data = redis.lrange(key, 0, -1)
            for piece in data:
                fd.write(piece)


if __name__ == '__main__':
    pass
