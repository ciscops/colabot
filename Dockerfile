FROM python:3.7-alpine

RUN apk update && apk upgrade && apk add bash && pip install -U pip
RUN apk add gcc
RUN apk add musl-dev

RUN adduser -D bot
WORKDIR /home/bot
COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
COPY cards cards/
COPY features features/
COPY webex webex/
COPY app.py app.py
COPY bot.py bot.py
COPY config.py config.py

COPY docker_boot.sh docker_boot.sh
RUN chmod +x docker_boot.sh
RUN chown -R bot:bot ./

USER bot
EXPOSE 3978
ENTRYPOINT ["./docker_boot.sh"]



