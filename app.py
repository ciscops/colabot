#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from config import DefaultConfig as CONFIG
from bot import COLABot
import pymongo
import json
import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# logging.basicConfig(filename='colabot_dev.log', format=FORMAT, level=logging.INFO)
logging.basicConfig(format=FORMAT, level=logging.INFO)
# logger = logging.getLogger(__name__)
# c_handler = logging.StreamHandler()
# f_handler = logging.FileHandler('colabot.log')
# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.INFO)
# c_format = logging.Formatter(FORMAT)
# f_format = logging.Formatter(FORMAT)
# c_handler.setFormatter(c_format)
# f_handler.setFormatter(f_format)
#
# logger.addHandler(c_handler)
# logger.addHandler(f_handler)


BOT = COLABot(webex_bot_token=CONFIG.ACCESS_TOKEN, webex_client_signing_secret=CONFIG.SECRET)


# Listen for incoming requests on /api/messages.
async def messages(req: Request) -> Response:
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
        logging.info(body)
    else:
        return Response(status=415)
    response = await BOT.process(req)
    if response:
        # return json_response(data=response.body, status=response.status)
        return Response(status=response['status_code'])
    return Response(status=201)


APP = web.Application()
APP.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    # First clear out any old conversations from the DB
    try:
        mongo_url = 'mongodb://' + CONFIG.MONGO_INITDB_ROOT_USERNAME + ':' + CONFIG.MONGO_INITDB_ROOT_PASSWORD + '@' + CONFIG.MONGO_SERVER + ':' + CONFIG.MONGO_PORT
        with pymongo.MongoClient(mongo_url) as client:
            db = client[CONFIG.MONGO_DB_ACTIVITY]
            posts = db[CONFIG.MONGO_COLLECTIONS_ACTIVITY]
            for post in posts.find():
                print(post)
            try:
                r = posts.delete_many({})
                d = dict((db, [collection for collection in client[db].list_collection_names()])
                         for db in client.list_database_names())
                print(json.dumps(d))
            except Exception as e:
                logger.error('Failed to connect to DB')
                logger.error(e)
    except:
        logger.error('Could not reach DB')

    # Second Run Web Server
    try:
        web.run_app(APP, host="0.0.0.0", port=CONFIG.WEB_PORT)
    except Exception as error:
        logger.warning('Failed to start web server')
        raise error
