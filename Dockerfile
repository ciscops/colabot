FROM node:13-alpine
RUN apk update && apk upgrade && apk add bash
RUN mkdir app
COPY . /app

RUN cd /app \
  && npm install

WORKDIR /app

EXPOSE 3000

CMD ["node", "bot.js"]
