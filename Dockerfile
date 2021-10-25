FROM python:3.8

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./config.py .
COPY ./main.py .
COPY ./redis_con.py .

RUN mkdir downloads
RUN mkdir temp