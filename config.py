# -*- coding: utf-8 -*-

import os


class DefaultConfig:
    """ Bot Configuration """
    WEB_PORT = os.environ['WEB_PORT']
    BOT_ID = os.environ['BOT_ID']
    BOT_NAME = os.environ['BOT_NAME']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    DIALOGUE_TIMEOUT = os.environ['DIALOGUE_TIMEOUT']
    SECRET = os.environ['SECRET']
    MONGO_INITDB_ROOT_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
    MONGO_INITDB_ROOT_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']
    MONGO_SERVER = os.environ['MONGO_SERVER']
    MONGO_PORT = os.environ['MONGO_PORT']
    MONGO_DB_ACTIVITY = os.environ['MONGO_DB_ACTIVITY']
    MONGO_COLLECTIONS_ACTIVITY = os.environ['MONGO_COLLECTIONS_ACTIVITY']
    SERVER_LIST = os.environ['SERVER_LIST']
    VIRL_USERNAME = os.environ['VIRL_USERNAME']
    VIRL_PASSWORD = os.environ['VIRL_PASSWORD']
    APPROVED_ORG_DOMAINS = os.environ['APPROVED_ORG_DOMAINS']
    MONGO_DB = os.environ['MONGO_DB']
    MONGO_COLLECTIONS = os.environ['MONGO_COLLECTIONS']