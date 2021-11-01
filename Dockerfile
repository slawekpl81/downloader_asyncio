FROM python:3.8

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./config.py .
COPY ./main.py .
COPY ./redis_con.py .
COPY ./app_methods.py .
COPY ./app_types.py .
COPY ./target_cls.py .
COPY ./test.py .

RUN mkdir downloads