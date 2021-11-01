from pydantic import BaseModel


class RespHead(BaseModel):
    resp_status: bool
    multiparts_download: bool
    file_size: float


if __name__ == '__main__':
    pass