FROM python:3.6
LABEL maintainer="Krzysztof Kaszanek"

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "run.py"]