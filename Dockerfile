FROM tiangolo/uwsgi-nginx-flask:python3.6
LABEL maintainer="Krzysztof Kaszanek"

COPY requirements.txt /tmp/
COPY ./app /app
RUN cd /app
RUN pip install -U pip && pip install -r /tmp/requirements.txt

ENV NGINX_WORKER_PROCESSES auto