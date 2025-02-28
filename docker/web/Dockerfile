# command in bash: docker build -t streamlit .
# app/Dockerfile 

FROM python:3.9-slim

WORKDIR /usr/src/app

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    clickhouse-client \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r requirements.txt

COPY ./ /usr/src/app

EXPOSE 8502 

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "Introduction.py", "--server.port=8502", "--server.address=0.0.0.0"]

