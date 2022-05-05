#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from config import DefaultConfig as CONFIG
from bot import COLABot


FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
# logging.basicConfig(filename='logfile.log', level=logging.INFO, format=FORMAT)

BOT = COLABot(webex_bot_token=CONFIG.ACCESS_TOKEN, webex_client_signing_secret=CONFIG.SECRET)


# Listening for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
        logging.info(body)
    else:
        return Response(status=415)
    response = await BOT.process(req)
    if response:
        return Response(status=response['status_code'])
    return Response(status=201)


APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="0.0.0.0", port=CONFIG.WEB_PORT)
    except Exception as error:
        logging.warning('Failed to start web server')
        raise error
