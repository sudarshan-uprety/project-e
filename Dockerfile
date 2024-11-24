FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /authentication_service

ADD . /authentication_service

COPY ./requirements.txt /authentication_service/requirements.txt

RUN pip3 install -r requirements.txt

RUN mkdir -p logs

COPY . /authentication_service

ENTRYPOINT [ "/bin/bash", "docker-entrypoint.sh" ]
