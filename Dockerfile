FROM python:3.8-alpine

RUN apk update && apk upgrade && apk add gcc && apk add musl-dev

RUN adduser -D bot
WORKDIR /home/bot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY cards cards/
COPY features features/
COPY webex webex/
COPY app.py app.py
COPY bot.py bot.py
COPY config.py config.py

RUN chown -R bot:bot ./
USER bot

ENTRYPOINT ["python3"]
CMD ["app.py"]




