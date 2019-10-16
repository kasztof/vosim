FROM ubuntu:18.10

RUN apt-get update -y && \
    apt-get install -y python3 python3-dev python3-pip
   
COPY ./requirements.txt /app/requirements.txt
COPY ./.env /app/.env

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app
RUN pwd
RUN ls -a
ENTRYPOINT ["python3"]

CMD ["vosim/__init__.py"]