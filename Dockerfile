FROM jasonking/webexbot:latest

# RUN cd /app \
#  && npm install request-promise 

WORKDIR /app

RUN rm -rf /app/skills/*

COPY /skills /app/skills/

CMD ["node", "bot.js"]
